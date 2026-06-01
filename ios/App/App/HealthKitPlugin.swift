import HealthKit
import Capacitor

@objc(HealthKitPlugin)
public class HealthKitPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "HealthKitPlugin"
    public let jsName = "HealthKitBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "requestAuth", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "getSteps", returnType: CAPPluginReturnPromise),
    ]

    private let healthStore = HKHealthStore()

    @objc func requestAuth(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable() else {
            call.resolve(["granted": false, "reason": "not_available"])
            return
        }
        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            call.resolve(["granted": false, "reason": "no_step_type"])
            return
        }
        healthStore.requestAuthorization(toShare: [], read: [stepType]) { granted, error in
            if let err = error {
                call.resolve(["granted": false, "reason": err.localizedDescription])
            } else {
                call.resolve(["granted": granted])
            }
        }
    }

    @objc func getSteps(_ call: CAPPluginCall) {
        guard HKHealthStore.isHealthDataAvailable(),
              let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            call.resolve(["steps": 0])
            return
        }
        let now = Date()
        let startOfDay = Calendar.current.startOfDay(for: now)
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: now, options: .strictStartDate)
        let query = HKStatisticsQuery(quantityType: stepType, quantitySamplePredicate: predicate, options: .cumulativeSum) { _, result, _ in
            let steps = result?.sumQuantity()?.doubleValue(for: HKUnit.count()) ?? 0
            call.resolve(["steps": Int(steps)])
        }
        healthStore.execute(query)
    }
}
