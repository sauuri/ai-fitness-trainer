import Capacitor
import Foundation

@objc(TimerBridgePlugin)
public class TimerBridgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "TimerBridgePlugin"
    public let jsName = "TimerBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "setTimer", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "clearTimer", returnType: CAPPluginReturnPromise),
    ]

    private let appGroup = "group.com.sauuri.nozeroday"

    @objc func setTimer(_ call: CAPPluginCall) {
        guard let endTime = call.getDouble("endTime") else {
            call.reject("endTime required"); return
        }
        let label = call.getString("label") ?? ""
        if let d = UserDefaults(suiteName: appGroup) {
            d.set(endTime, forKey: "timerEndTime")
            d.set(label,   forKey: "timerLabel")
            d.synchronize()
        }
        call.resolve()
    }

    @objc func clearTimer(_ call: CAPPluginCall) {
        if let d = UserDefaults(suiteName: appGroup) {
            d.removeObject(forKey: "timerEndTime")
            d.removeObject(forKey: "timerLabel")
            d.synchronize()
        }
        call.resolve()
    }
}
