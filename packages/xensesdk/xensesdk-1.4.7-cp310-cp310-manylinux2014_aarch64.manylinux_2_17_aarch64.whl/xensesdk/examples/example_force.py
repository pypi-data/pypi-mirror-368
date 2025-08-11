import sys
from xensesdk import ExampleView
from xensesdk import Sensor


def main():
    sensor_1 = Sensor.create('OG000232')
    sensor_0 = Sensor.createSolver("/home/msi/hongzhan_ws/gitlab/xensesdk/xensesdk/examples/xxxx")
    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Rectify, Sensor.OutputType.Marker2D, Sensor.OutputType.Depth)

    def callback():
        rec = sensor_1.selectSensorInfo(Sensor.OutputType.Rectify)
        force, res_force, mesh_init, diff, depth = sensor_0.selectSensorInfo(
            Sensor.OutputType.Force, 
            Sensor.OutputType.ForceResultant,
            Sensor.OutputType.Mesh3DInit,
            Sensor.OutputType.Difference, 
            Sensor.OutputType.Depth,
            rectify_image=rec
        )
        marker_img = sensor_0.drawMarkerMove(diff)
        View2d.setData(Sensor.OutputType.Rectify, rec)
        View2d.setData(Sensor.OutputType.Marker2D, marker_img)
        View2d.setData(Sensor.OutputType.Depth, depth)
        View.setForceFlow(force, res_force, mesh_init)
        View.setDepth(depth)

    View.setCallback(callback)
    View.show()
    sensor_0.release()
    sys.exit()

if __name__ == '__main__':
    main()