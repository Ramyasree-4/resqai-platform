import {
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  onAuthStateChanged as firebaseOnAuthStateChanged,
  type User as FirebaseUser,
  type Unsubscribe,
} from 'firebase/auth'
import { auth } from './config'

const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({ prompt: 'select_account' })

export async function signInWithGoogle(): Promise<{ user: FirebaseUser; token: string }> {
  const result = await signInWithPopup(auth, googleProvider)
  const token = await result.user.getIdToken()
  return { user: result.user, token }
}

export async function signOut(): Promise<void> {
  try {
    await firebaseSignOut(auth)
  } catch {
    // stub auth — ignore
  }
}

export function onAuthStateChanged(
  callback: (user: FirebaseUser | null) => void
): Unsubscribe {
  try {
    return firebaseOnAuthStateChanged(auth, callback)
  } catch {
    // Firebase not configured — call with null immediately
    callback(null)
    return () => {}
  }
}

export async function getIdToken(forceRefresh = false): Promise<string | null> {
  try {
    const user = auth.currentUser
    if (!user) return null
    return user.getIdToken(forceRefresh)
  } catch {
    return null
  }
}

export { auth }
