import ActivityKit
import Capacitor
import Foundation
import TimerShared
import UserNotifications
import WidgetKit

@objc(TimerBridgePlugin)
public class TimerBridgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "TimerBridgePlugin"
    public let jsName = "TimerBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "setTimer", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "clearTimer", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "updateTimer", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "pauseTimer", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "resumeTimer", returnType: CAPPluginReturnPromise),
    ]

    private let appGroup = "group.com.sauuri.nozeroday"

    @objc func setTimer(_ call: CAPPluginCall) {
        let exerciseName = call.getString("exerciseName") ?? ""
        let currentSet = call.getInt("currentSet") ?? 1
        let totalSets = call.getInt("totalSets") ?? 0
        let startTime = Date()
        let startMs = startTime.timeIntervalSince1970 * 1000

        if let d = UserDefaults(suiteName: appGroup) {
            d.set(startMs, forKey: "workoutStartTime")
            d.set(exerciseName, forKey: "exerciseName")
            d.set(currentSet, forKey: "currentSet")
            d.set(totalSets, forKey: "totalSets")
            d.synchronize()
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "NZDTimer")

        if #available(iOS 16.2, *) {
            Task { await startLiveActivity(startTime: startTime, exerciseName: exerciseName, currentSet: currentSet, totalSets: totalSets, call: call) }
        } else {
            call.resolve(["status": "ios_too_old"])
        }
    }

    @objc func updateTimer(_ call: CAPPluginCall) {
        let exerciseName = call.getString("exerciseName") ?? ""
        let currentSet = call.getInt("currentSet") ?? 1
        let totalSets = call.getInt("totalSets") ?? 0

        if let d = UserDefaults(suiteName: appGroup) {
            d.set(exerciseName, forKey: "exerciseName")
            d.set(currentSet, forKey: "currentSet")
            d.set(totalSets, forKey: "totalSets")
            d.synchronize()
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "NZDTimer")

        if #available(iOS 16.2, *) {
            Task {
                let existing = Activity<TimerActivityAttributes>.activities
                guard let activity = existing.first else { call.resolve(["status": "none"]); return }
                let state = TimerActivityAttributes.ContentState(
                    startTime: activity.content.state.startTime,
                    exerciseName: exerciseName, currentSet: currentSet, totalSets: totalSets
                )
                let content = ActivityContent(state: state, staleDate: nil)
                await activity.update(content)
                call.resolve(["status": "updated"])
            }
        } else {
            call.resolve(["status": "ios_too_old"])
        }
    }

    @objc func clearTimer(_ call: CAPPluginCall) {
        if let d = UserDefaults(suiteName: appGroup) {
            d.removeObject(forKey: "workoutStartTime")
            d.removeObject(forKey: "exerciseName")
            d.removeObject(forKey: "currentSet")
            d.removeObject(forKey: "totalSets")
            d.synchronize()
        }
        WidgetCenter.shared.reloadTimelines(ofKind: "NZDTimer")

        if #available(iOS 16.2, *) {
            Task {
                for activity in Activity<TimerActivityAttributes>.activities {
                    await activity.end(nil, dismissalPolicy: .immediate)
                }
                call.resolve()
            }
        } else {
            call.resolve()
        }
    }

    @objc func pauseTimer(_ call: CAPPluginCall) {
        let elapsed = call.getInt("elapsedSeconds") ?? 0
        if #available(iOS 16.2, *) {
            Task {
                guard let activity = Activity<TimerActivityAttributes>.activities.first else {
                    call.resolve(["status": "none"]); return
                }
                var s = activity.content.state
                s.isPaused = true
                s.elapsedSeconds = elapsed
                let content = ActivityContent(state: s, staleDate: nil)
                await activity.update(content)
                call.resolve(["status": "paused"])
            }
        } else { call.resolve() }
    }

    @objc func resumeTimer(_ call: CAPPluginCall) {
        let elapsed = call.getInt("elapsedSeconds") ?? 0
        if #available(iOS 16.2, *) {
            Task {
                guard let activity = Activity<TimerActivityAttributes>.activities.first else {
                    call.resolve(["status": "none"]); return
                }
                var s = activity.content.state
                s.isPaused = false
                s.elapsedSeconds = elapsed
                s.startTime = Date().addingTimeInterval(-Double(elapsed))
                let content = ActivityContent(state: s, staleDate: nil)
                await activity.update(content)
                call.resolve(["status": "resumed"])
            }
        } else { call.resolve() }
    }

    @available(iOS 16.2, *)
    private func startLiveActivity(startTime: Date, exerciseName: String, currentSet: Int, totalSets: Int, call: CAPPluginCall) async {
        let info = ActivityAuthorizationInfo()
        guard info.areActivitiesEnabled else {
            call.resolve(["status": "disabled"]); return
        }

        for activity in Activity<TimerActivityAttributes>.activities {
            await activity.end(nil, dismissalPolicy: .immediate)
        }

        let state = TimerActivityAttributes.ContentState(
            startTime: startTime, exerciseName: exerciseName,
            currentSet: currentSet, totalSets: totalSets
        )
        let content = ActivityContent(state: state, staleDate: nil)

        do {
            let activity = try Activity.request(attributes: TimerActivityAttributes(), content: content, pushType: nil)
            call.resolve(["status": "started", "id": activity.id])
        } catch {
            call.resolve(["status": "error", "detail": error.localizedDescription])
        }
    }
}
