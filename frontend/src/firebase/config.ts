import { initializeApp, getApps, type FirebaseApp } from 'firebase/app'
import { getAuth, type Auth } from 'firebase/auth'

const apiKey = import.meta.env.VITE_FIREBASE_API_KEY ?? ''
const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID ?? ''

// Detect placeholder / missing config
const isConfigured =
  apiKey.length > 10 &&
  !apiKey.startsWith('placeholder') &&
  !apiKey.startsWith('your-') &&
  projectId.length > 3

let app: FirebaseApp
let auth: Auth

if (isConfigured) {
  const firebaseConfig = {
    apiKey,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  }
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
  auth = getAuth(app)
} else {
  // Dev mode without Firebase — create a stub so imports don't crash
  console.warn(
    '[ResQAI] Firebase not configured. Add VITE_FIREBASE_API_KEY to frontend/.env\n' +
    'Get it from: Firebase Console → Project Settings → General → Web API Key'
  )
  // Create a minimal app with a dummy config so getAuth() doesn't throw
  try {
    app = getApps().length === 0
      ? initializeApp({ apiKey: 'stub', projectId: 'stub', appId: 'stub' })
      : getApps()[0]
    auth = getAuth(app)
  } catch {
    // absolute fallback — cast to avoid TS error
    app = {} as FirebaseApp
    auth = {} as Auth
  }
}

export { app, auth }
export default app
