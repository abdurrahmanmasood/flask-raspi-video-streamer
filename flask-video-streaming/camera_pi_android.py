import io
import time
import picamera
from base_camera import BaseCamera
# from threading import Condition

CAMERA_MAP = {}
USER_STOP_LIST = set()


# Taken from picamera.readthedocs.io section 4.10
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        # self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            # with self.condition:
            self.frame = self.buffer.getvalue()
                # self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class Camera(BaseCamera):
    uid = None

    def __init__(self, uid=None):
        self.uid = uid

        if self.uid in CAMERA_MAP:
            self.camera = CAMERA_MAP[self.uid].camera
            self.output = CAMERA_MAP[self.uid].output
        else:
            self.output = StreamingOutput()
            self.camera = picamera.PiCamera(sensor_mode=5, resolution="1640x922", framerate=40)

        super(Camera, self).__init__()

    def frames(self):
        # # let camera warm up
        # time.sleep(2)

        # stream = StreamingOutput ()
        # for foo in camera.capture_continuous(stream, 'jpeg',
        #                                      use_video_port=True):
        #     # return current frame
        #     stream.seek(0)
        #     yield stream.read()

        #     # reset stream for next frame
        #     stream.seek(0)
        #     stream.truncate()
        self.camera.start_recording(self.output, format='mjpeg')

        if self.uid is not None:
            print("Adding camera for user: {}.".format(self.uid))
            CAMERA_MAP[self.uid] = self

        print(CAMERA_MAP)
        
        try:
            while True:
                # with output.condition:
                    # output.condition.wait()
                frame = self.output.frame
                yield frame
                # self.wfile.write(b'--FRAME\r\n')
                # self.send_header('Content-Type', 'image/jpeg')
                # self.send_header('Content-Length', len(frame))
                # self.end_headers()
                # self.wfile.write(frame)
                # self.wfile.write(b'\r\n')
        except Exception as e:
            print('Error streaming frames: {0}.'.format(e))
        finally:
            print ('Closing and deleting camera instance.')
            self.camera.close()
            if self.uid is not None:
                del CAMERA_MAP[self.uid]

                # Note: We do not remove the uid from the user stop list to make
                #       sure we don't re-enable the camera when a user stops
                #       using the app. This could cause issues later so we should
                #       probably ping the user the next time they open the app
                #       to tell them to re-enable.
                # if self.uid in USER_STOP_LIST:
                #     USER_STOP_LIST.remove(self.uid)

                print('\nCamera Map: {}\n'.format(CAMERA_MAP))
                print('\nUser Stop List: {}\n'.format(USER_STOP_LIST))
