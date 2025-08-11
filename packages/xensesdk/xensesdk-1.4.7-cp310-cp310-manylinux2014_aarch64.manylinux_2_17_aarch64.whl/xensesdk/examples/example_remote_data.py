import sys
from xensesdk import ExampleView
from xensesdk import Sensor
from xensesdk import call_service


def main():
    MASTERP_IP = "192.168.99.2"
    
    # find all sensors
    ret = call_service(MASTERP_IP, "MasterService", "scan_sensor_sn")
    if ret["success"] is False:
        print(f"Failed to scan sensors: {ret['ret']}")
        sys.exit(1)
    else:
        print(f"Found sensors: {ret['ret']}, using the first one.")
    serial_number = list(ret["ret"].keys())[0]

    # create a sensor
    sensor_0 = Sensor.create(serial_number, ip_address=MASTERP_IP)
    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Difference, Sensor.OutputType.Depth)
    

    def callback():
        force, res_force, mesh_init, diff, depth = sensor_0.selectSensorInfo(
            Sensor.OutputType.Force, 
            Sensor.OutputType.ForceResultant,
            Sensor.OutputType.Mesh3DInit,
            Sensor.OutputType.Difference, 
            Sensor.OutputType.Depth
        )
        marker_img = sensor_0.drawMarkerMove(diff)
        # View2d.setData(Sensor.OutputType.Rectify, rec)
        # View2d.setData(Sensor.OutputType.Marker2D, marker_img)
        View2d.setData(Sensor.OutputType.Depth, depth)
        View.setForceFlow(force, res_force, mesh_init)
        View.setDepth(depth)
    View.setCallback(callback)

    View.show()
    sensor_0.release()
    sys.exit()


if __name__ == '__main__':
    main()