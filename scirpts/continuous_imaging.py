"""
Continuous imaging
Opens a camera, adjusts settings, and polls for images with a live OpenCV preview.

Additional features:
  1. Save single frames ('s') and toggle video recording ('r')
  2. Live exposure/gain control via OpenCV trackbars
"""
import numpy as np
import os
import cv2
import time
from datetime import datetime
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE

WINDOW_NAME = "Image From TSI Cam"
OUTPUT_DIR = "captures"


def make_output_dir():
    """Make folder for saved images/videos if it doesn't already exist."""
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def nothing(_value):
    """Required no-op callback for OpenCV trackbars."""
    pass


with TLCameraSDK() as sdk:
    available_cameras = sdk.discover_available_cameras()
    if len(available_cameras) < 1:
        print("no cameras detected")
        exit()

    # setup camera for continuous imaging
    with sdk.open_camera(available_cameras[0]) as camera:
        camera.exposure_time_us = 10000  # set exposure to 10 ms 
        camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
        camera.image_poll_timeout_ms = 1000  # how long get_pending_frame_or_null() will wait for a frame (in ms)
        camera.frame_rate_control_value = 10 # target frame rate in frames per second
        camera.is_frame_rate_control_enabled = True # enforce the frame rate cap above
        
        camera.arm(2)
        camera.issue_software_trigger() # start acquisition

        make_output_dir() # setup the "captures" folder

        # live exposure controls
        cv2.namedWindow(WINDOW_NAME) # create the preview window to add trackbars
        exposure_range = camera.exposure_time_range_us # fetch camera's valid exposure range (min/max in us)

        # create a slider for exposure (trackbars only support integers)
        cv2.createTrackbar(
            "Exposure (us)", 
            WINDOW_NAME,
            camera.exposure_time_us, # starting position = current exposure
            exposure_range.max, # trackbar max = camera's maximum supported exposure
            nothing
        )

        # set the trackbar's minimum to the camera's minimum supported exposurs (min value is 1)
        cv2.setTrackbarMin("Exposure (us)", WINDOW_NAME, max(1, exposure_range.min))

        # recording state
        video_writer = None # will hold a cv2.VideoWriter object once recording starts
        is_recording = False

        try:
            while True:
                # poll the camera for the next available frame
                frame = camera.get_pending_frame_or_null()
                if frame is None:
                    continue    

                # copy the pixel buffer out of the frame to keep working on it
                image_buffer_copy = np.copy(frame.image_buffer)

                # reshape the flat buffer into a 2D (height x width) image
                numpy_shaped_image = image_buffer_copy.reshape(
                    camera.image_height_pixels, camera.image_width_pixels)
                
                # build a 3-channel image for OpenCV display (OpenCV expects BGR images)
                nd_image_array = np.full(
                    (camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)
                nd_image_array[:, :, 0] = numpy_shaped_image # blue
                nd_image_array[:, :, 1] = numpy_shaped_image # green
                nd_image_array[:, :, 2] = numpy_shaped_image # red

                # frame info
                overlay_text = "Frame #{}".format(frame.frame_count)
                cv2.putText(nd_image_array, overlay_text, (10, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # add REC overlay if recording
                if is_recording:
                    cv2.putText(nd_image_array, "REC", (10, 55),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # display image in OpenCV window
                cv2.imshow(WINDOW_NAME, nd_image_array)

                # write to video file if recording
                if is_recording and video_writer is not None:
                    video_writer.write(nd_image_array)

                # handle user input waiting for 1 ms
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    print("Closing application.")
                    break

                # take image snapshot
                elif key == ord('s'):
                    filename = os.path.join(
                        OUTPUT_DIR, "frame_{}.png".format(datetime.now().strftime("%Y%m%d_%H%M%S_%f")))
                    cv2.imwrite(filename, nd_image_array)
                    print("Saved snapshot: {}".format(filename))

                # enter recording mode
                elif key == ord('r'):
                    if not is_recording:
                        # start new recording with a timestamped .avi file and a VideoWriter
                        filename = os.path.join(
                            OUTPUT_DIR, "recording_{}.avi".format(datetime.now().strftime("%Y%m%d_%H%M%S")))
                        fourcc = cv2.VideoWriter_fourcc(*"XVID")
                        video_writer = cv2.VideoWriter(
                            filename, fourcc, 10, # 10 frames per second for the output file
                            (camera.image_width_pixels, camera.image_height_pixels))
                        is_recording = True
                        print("Started recording: {}".format(filename))
                    else:
                        is_recording = False
                        if video_writer is not None:
                            video_writer.release()
                            video_writer = None
                        print("Stopped recording.")

                # apply live exposure changes from trackbars after each frame
                trackbar_exposure = cv2.getTrackbarPos("Exposure (us)", WINDOW_NAME)
                if trackbar_exposure != camera.exposure_time_us:
                    camera.exposure_time_us = trackbar_exposure

        except KeyboardInterrupt:
            print("loop terminated")

        finally:
            if video_writer is not None:
                video_writer.release() # finish the video writer if it was active
            cv2.destroyAllWindows() # close the OpenCV preview window
            camera.disarm() # stop the camera's acquisition

#  Because we are using the 'with' statement context-manager, disposal has been taken care of.
print("program completed")