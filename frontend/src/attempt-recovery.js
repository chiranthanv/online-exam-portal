const DATABASE = "oep-attempt-recovery";
const STORE = "pending-answers";
const VERSION = 1;

function openDatabase() {
  if (!globalThis.indexedDB) {
    return Promise.reject(new Error("This browser does not support offline answer recovery."));
  }
  return new Promise((resolve, reject) => {
    const request = globalThis.indexedDB.open(DATABASE, VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: "exam_id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("Could not open local recovery storage."));
    request.onblocked = () => reject(new Error("Local recovery storage is blocked by another tab."));
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
          reject(tx.error || new Error("Local answer recovery transaction failed."));
        };
        tx.onabort = () => {
          db.close();
          reject(tx.error || new Error("Local answer recovery transaction was aborted."));
        };
      }),
  );
}

export function savePendingAnswers(examId, answers, now = Date.now()) {
  if (!examId || !answers || typeof answers !== "object" || Array.isArray(answers)) {
    return Promise.reject(new TypeError("A valid exam ID and pending-answer map are required."));
  }
  if (!Object.keys(answers).length) {
    return transaction("readwrite", (store) => store.delete(examId));
  }
  // Only answer values and their local save time are persisted. No JWT, user ID,
  // attempt session UUID, or other authentication/session credential is stored.
  const record = {
    exam_id: examId,
    version: VERSION,
    answers: { ...answers },
    updated_at: now,
  };
  return transaction("readwrite", (store) => store.put(record));
}

export function loadPendingAnswers(examId, now = Date.now()) {
  return transaction("readonly", (store) => store.get(examId)).then((record) => {
    if (
      !record ||
      record.version !== VERSION ||
      !record.answers ||
      typeof record.answers !== "object" ||
      Array.isArray(record.answers)
    ) {
      return { answers: {}, age_ms: null, clock_skew: false };
    }
    const age = now - Number(record.updated_at);
    return {
      answers: record.answers,
      age_ms: Number.isFinite(age) && age >= 0 ? age : null,
      clock_skew: !Number.isFinite(age) || age < 0,
    };
  });
}

export function clearPendingAnswers(examId) {
  return transaction("readwrite", (store) => store.delete(examId));
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
