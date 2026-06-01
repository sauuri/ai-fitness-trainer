import ActivityKit
import UIKit
import Capacitor
import TimerShared
import UserNotifications
import WidgetKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {}
    func applicationDidEnterBackground(_ application: UIApplication) {}
    func applicationWillEnterForeground(_ application: UIApplication) {}

    func applicationDidBecomeActive(_ application: UIApplication) {
        if #available(iOS 16.2, *) {
            Task {
                for activity in Activity<TimerActivityAttributes>.activities {
                    if activity.activityState == .ended {
                        await activity.end(nil, dismissalPolicy: .immediate)
                    }
                }
            }
        }
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // UserDefaults 위젯 데이터 정리
        if let d = UserDefaults(suiteName: "group.com.sauuri.nozeroday") {
            d.removeObject(forKey: "workoutStartTime")
            d.removeObject(forKey: "exerciseName")
            d.removeObject(forKey: "currentSet")
            d.removeObject(forKey: "totalSets")
            d.synchronize()
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "NZDTimer")

        // Live Activity 즉시 종료 (semaphore로 async 완료 대기)
        if #available(iOS 16.2, *) {
            let semaphore = DispatchSemaphore(value: 0)
            Task.detached {
                for activity in Activity<TimerActivityAttributes>.activities {
                    await activity.end(nil, dismissalPolicy: .immediate)
                }
                semaphore.signal()
            }
            _ = semaphore.wait(timeout: .now() + 3)
        }
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }
}
