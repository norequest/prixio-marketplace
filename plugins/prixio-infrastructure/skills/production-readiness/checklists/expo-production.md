# Expo Mobile App Production Checklist

Applies to: **Courio Courier App**, **Courio Consumer App**

---

## Build & Release

- [ ] EAS Build profiles (development, preview, production)
- [ ] OTA updates configured (EAS Update)
- [ ] App signing keys securely stored
- [ ] Version numbering strategy (semver)
- [ ] App store metadata prepared (screenshots, descriptions in ka/en)
- [ ] Privacy policy and terms of service URLs configured

## Performance

- [ ] App startup time < 2 seconds
- [ ] No unnecessary re-renders (React DevTools profiling)
- [ ] Optimized images and assets
- [ ] Background location tracking battery-optimized (Courio courier)
- [ ] FlatList/FlashList for long lists (no ScrollView for dynamic content)
- [ ] Memory leak checks (unmounted component subscriptions)
- [ ] Hermes engine enabled

## Security

- [ ] API keys not hardcoded (use expo-constants or env)
- [ ] Certificate pinning for API calls
- [ ] Secure storage for tokens (expo-secure-store)
- [ ] Deep link validation
- [ ] Jailbreak/root detection (optional but recommended)
- [ ] Obfuscation enabled for production builds
- [ ] No sensitive data in AsyncStorage (use SecureStore)

## Push Notifications

- [ ] FCM configured and tested
- [ ] Notification permissions handled gracefully
- [ ] Background notification handling
- [ ] Notification categories for different events
- [ ] Notification tap navigation works correctly
- [ ] Silent push for data sync (order updates)

## Location Services (Courier App)

- [ ] Background location permission requested with clear rationale
- [ ] Location accuracy appropriate for use case (balanced vs high)
- [ ] Geofencing for delivery zone awareness
- [ ] Location updates batched to reduce battery drain
- [ ] Graceful degradation when location permission denied

## Offline Support

- [ ] Offline queue for actions (delivery status updates)
- [ ] Network status indicator in UI
- [ ] Cached data displayed when offline
- [ ] Sync mechanism when connectivity restored
- [ ] Conflict resolution strategy for offline edits

## Testing

- [ ] Unit tests for business logic
- [ ] Integration tests for critical flows (login, order acceptance, delivery)
- [ ] E2E tests with Detox or Maestro
- [ ] Device matrix testing (Android 10+, iOS 15+)
- [ ] Crash reporting enabled (Sentry or Crashlytics)
