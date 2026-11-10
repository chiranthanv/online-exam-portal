const DATABASE = "oep-attempt-recovery";
// Preserve old unscoped records, but never apply one to another account's attempt.
const STORE = "pending-attempt-answers";
const VERSION = 2;

function openDatabase() {
  if (!globalThis.indexedDB) {
    return Promise.reject(
      new Error("This browser does not support offline answer recovery."),
    );
  }
  return new Promise((resolve, reject) => {
    const request = globalThis.indexedDB.open(DATABASE, VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: "attempt_id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () =>
      reject(
        request.error || new Error("Could not open local recovery storage."),
      );
    request.onblocked = () =>
      reject(new Error("Local recovery storage is blocked by another tab."));
  });
}

function transaction(mode, action) {
  return openDatabase().then(
    (db) =>
      new Promise((resolve, reject) => {
        let result;
        const tx = db.transaction(STORE, mode);
        const store = tx.objectStore(STORE);
        try {
          result = action(store);
        } catch (error) {
          db.close();
          reject(error);
          return;
        }
        tx.oncomplete = () => {
          db.close();
          resolve(result?.result);
        };
        tx.onerror = () => {
          db.close();
          reject(
            tx.error || new Error("Local answer recovery transaction failed."),
          );
        };
        tx.onabort = () => {
          db.close();
          reject(
            tx.error ||
              new Error("Local answer recovery transaction was aborted."),
          );
        };
      }),
  );
}

export function savePendingAnswers(
  examId,
  attemptId,
  answers,
  now = Date.now(),
) {
  if (
    !examId ||
    !attemptId ||
    !answers ||
    typeof answers !== "object" ||
    Array.isArray(answers)
  ) {
    return Promise.reject(
      new TypeError("A valid exam ID and pending-answer map are required."),
    );
  }

  if (!Object.keys(answers).length) {
    return transaction("readwrite", (store) => store.delete(attemptId));
  }

  const changedAt = Number.isFinite(now) ? now : Date.now();

  return transaction("readwrite", (store) => {
    const request = store.get(attemptId);

    request.onsuccess = () => {
      const previous = request.result;

      const previousMatches =
        previous?.version === VERSION &&
        previous.exam_id === examId &&
        previous.attempt_id === attemptId &&
        previous.answers &&
        typeof previous.answers === "object" &&
        !Array.isArray(previous.answers);

      const previousTimestamps =
        previous?.saved_at_by_question &&
        typeof previous.saved_at_by_question === "object" &&
        !Array.isArray(previous.saved_at_by_question)
          ? previous.saved_at_by_question
          : null;

      const legacyTimestamp =
        typeof previous?.updated_at === "number" &&
        Number.isFinite(previous.updated_at)
          ? previous.updated_at
          : null;

      const savedAtByQuestion = {};

      for (const [questionId, optionId] of Object.entries(answers)) {
        const unchanged =
          previousMatches &&
          Object.prototype.hasOwnProperty.call(previous.answers, questionId) &&
          previous.answers[questionId] === optionId;

        const questionTimestamp = previousTimestamps?.[questionId];
        const previousTimestamp =
          typeof questionTimestamp === "number" &&
          Number.isFinite(questionTimestamp)
            ? questionTimestamp
            : legacyTimestamp;

        savedAtByQuestion[questionId] =
          unchanged &&
          typeof previousTimestamp === "number" &&
          Number.isFinite(previousTimestamp)
            ? previousTimestamp
            : changedAt;
      }

      const record = {
        exam_id: examId,
        attempt_id: attemptId,
        version: VERSION,
        answers: { ...answers },
        updated_at: changedAt,
        saved_at_by_question: savedAtByQuestion,
      };

      store.put(record);
    };

    return request;
  });
}

export function loadPendingAnswers(examId, attemptId, now = Date.now()) {
  if (!examId || !attemptId) {
    return Promise.reject(
      new TypeError("An exam and attempt ID are required."),
    );
  }

  return transaction("readonly", (store) => store.get(attemptId)).then(
    (record) => {
      if (
        !record ||
        record.version !== VERSION ||
        record.exam_id !== examId ||
        !record.answers ||
        typeof record.answers !== "object" ||
        Array.isArray(record.answers)
      ) {
        return {
          answers: {},
          age_ms: null,
          saved_at: null,
          clock_skew: false,
          age_ms_by_question: {},
          saved_at_by_question: {},
        };
      }

      const hasPerAnswerTimestamps =
        record.saved_at_by_question &&
        typeof record.saved_at_by_question === "object" &&
        !Array.isArray(record.saved_at_by_question);

      const savedAtByQuestion = {};
      const ageMsByQuestion = {};
      let clockSkew = false;

      for (const questionId of Object.keys(record.answers)) {
        const candidate = hasPerAnswerTimestamps
          ? record.saved_at_by_question[questionId]
          : record.updated_at;

        const savedAt =
          typeof candidate === "number" && Number.isFinite(candidate)
            ? candidate
            : null;

        if (savedAt === null) {
          clockSkew = true;
          continue;
        }

        savedAtByQuestion[questionId] = savedAt;

        const age = now - savedAt;

        if (Number.isFinite(age) && age >= 0) {
          ageMsByQuestion[questionId] = age;
        } else {
          clockSkew = true;
        }
      }

      const timestamps = Object.values(savedAtByQuestion);
      const oldestSavedAt = timestamps.length ? Math.min(...timestamps) : null;

      const oldestAge =
        oldestSavedAt === null ? Number.NaN : now - oldestSavedAt;

      return {
        answers: record.answers,
        age_ms:
          !clockSkew && Number.isFinite(oldestAge) && oldestAge >= 0
            ? oldestAge
            : null,
        saved_at: oldestSavedAt,
        clock_skew: clockSkew,
        age_ms_by_question: ageMsByQuestion,
        saved_at_by_question: savedAtByQuestion,
      };
    },
  );
}

export function clearPendingAnswers(examId, attemptId) {
  if (!examId || !attemptId)
    return Promise.reject(
      new TypeError("An exam and attempt ID are required."),
    );
  return transaction("readwrite", (store) => store.delete(attemptId));
}

export function formatRecoveryAge(ageMs) {
  if (!Number.isFinite(ageMs) || ageMs < 0) return "age unavailable";
  const seconds = Math.floor(ageMs / 1000);
  if (seconds < 60) return "less than a minute ago";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute(s) ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `${hours} hour(s) ago`;
  return `${Math.floor(hours / 24)} day(s) ago`;
}
