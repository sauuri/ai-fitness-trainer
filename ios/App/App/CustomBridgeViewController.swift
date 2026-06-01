import Capacitor

class CustomBridgeViewController: CAPBridgeViewController {
    override func capacitorDidLoad() {
        bridge?.registerPluginInstance(TimerBridgePlugin())
    }
}
