import { useState, useEffect, useCallback } from 'react'

interface GeolocationState {
  latitude: number | null
  longitude: number | null
  accuracy: number | null
  error: string | null
  loading: boolean
}

export function useGeolocation(watchPosition = false) {
  const [state, setState] = useState<GeolocationState>({
    latitude: null,
    longitude: null,
    accuracy: null,
    error: null,
    loading: false,
  })

  const getCurrentPosition = useCallback(() => {
    if (!navigator.geolocation) {
      setState((s) => ({
        ...s,
        error: 'Geolocation is not supported by your browser',
        loading: false,
      }))
      return
    }

    setState((s) => ({ ...s, loading: true, error: null }))

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          error: null,
          loading: false,
        })
      },
      (err) => {
        let message = 'Unable to get location'
        switch (err.code) {
          case err.PERMISSION_DENIED:
            message = 'Location permission denied'
            break
          case err.POSITION_UNAVAILABLE:
            message = 'Location information is unavailable'
            break
          case err.TIMEOUT:
            message = 'Location request timed out'
            break
        }
        setState((s) => ({ ...s, error: message, loading: false }))
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    )
  }, [])

  useEffect(() => {
    if (!watchPosition) return

    if (!navigator.geolocation) {
      setState((s) => ({
        ...s,
        error: 'Geolocation is not supported by your browser',
      }))
      return
    }

    setState((s) => ({ ...s, loading: true }))

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        setState({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          error: null,
          loading: false,
        })
      },
      (err) => {
        setState((s) => ({ ...s, error: err.message, loading: false }))
      },
      { enableHighAccuracy: true }
    )

    return () => navigator.geolocation.clearWatch(watchId)
  }, [watchPosition])

  return { ...state, getCurrentPosition }
}
