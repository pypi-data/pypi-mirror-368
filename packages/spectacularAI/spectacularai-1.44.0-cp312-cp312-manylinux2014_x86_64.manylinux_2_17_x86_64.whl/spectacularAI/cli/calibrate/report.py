import json
import pathlib

from .html import generateHtml

def advancedArgs(f):
    # Thresholds for passing checks.
    f("--coverage_threshold_monocular", type=float, default=0.8, help="Coverage check pass threshold")
    f("--coverage_threshold_stereo", type=float, default=0.7, help="Coverage check pass threshold")
    f("--reprojection_threshold", type=float, default=0.8, help="Reprojection check pass threshold for camera phase")
    f("--reprojection_threshold_imu", type=float, default=1.5, help="Reprojection check pass threshold for IMU phase")
    # You can probably leave these to the default values.
    f("--bucket_count_vertical", type=int, default=10, help="Coverage check resolution")
    f("--bucket_full_count_monocular", type=int, default=30, help="Coverage check bucket threshold")
    f("--bucket_full_count_stereo", type=int, default=20, help="Coverage check bucket threshold")
    f("--camera_max_rel_position_change", type=float, default=0.05, help="Extrinsics check relative camera-to-camera position change threshold")
    f("--imu_max_rel_position_change", type=float, default=0.2, help="Extrinsics check relative IMU-to-camera position change threshold")
    f("--camera_max_angle_change_degrees", type=float, default=1, help="Extrinsics check camera angle change threshold")
    f("--verbose_report", default=False, action="store_true", help="Add extra details to HTML report.")

def define_args(parser, include_advanced=False):
    parser.add_argument("--output_html", type=pathlib.Path, help="Path to calibration report HTML output.")
    parser.add_argument("--output_json", type=pathlib.Path, help="Path to JSON output.")

    if include_advanced:
        def f(name, **kwargs):
            parser.add_argument(name, **kwargs)
        advancedArgs(f)

def addDefaultsForAdvanced(args):
    def f(name, default, **kwargs):
        _, __, withoutDashes = name.partition('--')
        assert len(withoutDashes) > 0
        if not hasattr(args, withoutDashes):
            setattr(args, withoutDashes, default)
    advancedArgs(f)

def clamp(x, minValue, maxValue):
    if x < minValue: return minValue
    if x > maxValue: return maxValue
    return x

def readJson(filePath):
    with open(filePath) as f:
        return json.load(f)

def radToDeg(a):
    import numpy as np
    return a / np.pi * 180

def angle(vec1, vec2):
    import numpy as np
    return np.arccos(np.dot(vec1, vec2))

def computeVergenceDegrees(imuToCam0, imuToCam1):
    # Principal axis in IMU coordinates
    def axis(imuToCam):
        camToImuRot = imuToCam[:3, :3].transpose()
        return camToImuRot[:, 2]
    return radToDeg(angle(axis(imuToCam0), axis(imuToCam1)))

def computeBaseline(imuToCam0, imuToCam1):
    import numpy as np
    cam0ToCam1 = imuToCam1 @ np.linalg.inv(imuToCam0)
    return np.linalg.norm(cam0ToCam1[:3, 3])

def base64(fig):
    import matplotlib.pyplot as plt
    import io
    import base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def scatterFrame(args, xy, width, height, name, title):
    import matplotlib.pyplot as plt
    import numpy as np
    rect = np.array([[0, 0], [width, 0], [width, height], [0, height], [0, 0]])

    fig, ax = plt.subplots()
    if xy.size > 0:
        ax.scatter(xy[:, 0], xy[:, 1], c="blue", marker="o", alpha=0.3, s=2)
    ax.plot(rect[:, 0], rect[:, 1], color="black", linewidth=2)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("equal")
    ax.axis("off")
    ax.margins(x=0, y=0)
    fig.tight_layout()
    image = base64(fig)
    return image

def scatterReprojection(args, xy, errors, width, height, name, threshold):
    import matplotlib.pyplot as plt
    import numpy as np
    errors = np.minimum(errors, threshold)

    fig, ax = plt.subplots()
    rect = np.array([[0, 0], [width, 0], [width, height], [0, height], [0, 0]])
    ax.scatter(xy[:, 0], xy[:, 1], c=errors, marker="o", alpha=0.3, s=2, cmap="jet")
    ax.plot(rect[:, 0], rect[:, 1], color="black", linewidth=2)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("equal")
    ax.axis("off")
    ax.margins(x=0, y=0)
    fig.tight_layout()
    # ax.colorbar(label="Error")

    image = base64(fig)
    return image

def bucketCount(args, xy, width, height, name, title, fullCount):
    import matplotlib.pyplot as plt
    import numpy as np
    bucketCountHorizontal = round(width / height * args.bucket_count_vertical)

    v = np.zeros(shape=(args.bucket_count_vertical, bucketCountHorizontal))

    for i in range(xy.shape[0]):
        x = clamp(int(xy[i, 0] / width * bucketCountHorizontal), 0, bucketCountHorizontal - 1)
        y = clamp(int(xy[i, 1] / height * args.bucket_count_vertical), 0, args.bucket_count_vertical - 1)
        v[y, x] += 1

    v = np.minimum(v, fullCount)
    coverage = np.sum(v == fullCount) / (bucketCountHorizontal * args.bucket_count_vertical)
    v /= fullCount

    fig, ax = plt.subplots()
    ax.imshow(v, cmap='gray', origin='upper', vmin=0, vmax=1)
    # plt.colorbar(label="Value")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.margins(x=0, y=0)
    fig.tight_layout()
    image = base64(fig)
    return coverage, image

def appendCoverage(output, cameraInds, images, ret, threshold):
    if not "coverage" in output: output["coverage"] = []
    passed = bool(ret >= threshold)
    output["coverage"].append({
        "cameraInds": cameraInds,
        "images": images,
        "bucketsCoverage": ret,
        "threshold": threshold,
        "passed": passed,
    })
    if not passed: output["passed"] = False

def appendReprojection(args, output, key, cameraInds, images, errorCam, errorCamImu):
    if not key in output: output[key] = []

    passedCam = bool(errorCam < args.reprojection_threshold)
    passedCamImu = bool(errorCamImu is None or errorCamImu < args.reprojection_threshold_imu)
    passed = passedCam and passedCamImu
    output[key].append({
        "cameraInds": cameraInds,
        "images": images,
        "errorCam": errorCam,
        "errorCamImu": errorCamImu,
        "thresholdCam": args.reprojection_threshold,
        "thresholdCamImu": args.reprojection_threshold_imu,
        "passed": passed,
    })
    if not passed: output["passed"] = False

def mergeCoordinates(data, cameraInd, xKey, yKey, requiredKey=None):
    import numpy as np
    x = []
    y = []
    for frame in data:
        if frame["camera_ind"] != cameraInd: continue
        if requiredKey and requiredKey not in frame: continue
        x.extend(frame[xKey])
        y.extend(frame[yKey])
    assert(len(x) == len(y))
    return np.vstack((np.array(x), np.array(y))).transpose()

def mergeErrors(data, cameraInd, key):
    import numpy as np
    errors = []
    for frame in data:
        if frame["camera_ind"] != cameraInd: continue
        if not key in frame: continue
        errors.extend(frame[key])
    return np.array(errors)

def compute(args, data, detectedDict, width, height, cameraInd, output):
    import numpy as np

    xy = mergeCoordinates(data, cameraInd, "detected_px", "detected_py")

    image0 = scatterFrame(args, xy, width, height, f"scatter{cameraInd}", f"Detected in camera {cameraInd}")
    ret, image1 = bucketCount(args, xy, width, height, f"bucket{cameraInd}", "Number of detections in each bucket (white is good)", args.bucket_full_count_monocular)
    appendCoverage(output, [cameraInd], [image0, image1], ret, args.coverage_threshold_monocular)

    errorsCam = mergeErrors(data, cameraInd, "error_cam")
    image0 = scatterReprojection(args, xy, errorsCam, width, height, f"reprojection-cam{cameraInd}",
        args.reprojection_threshold)
    meanErrorCam = errorsCam.mean() if errorsCam.size > 0 else 0

    meanErrorCamImu = None
    images = [image0]
    errorsCamImu = mergeErrors(data, cameraInd, "error_cam_imu")
    if len(errorsCamImu) > 0:
        xyImu = mergeCoordinates(data, cameraInd, "detected_px", "detected_py", "error_cam_imu")
        image1 = scatterReprojection(args, xyImu, errorsCamImu, width, height, f"reprojection-cam{cameraInd}-IMU",
            args.reprojection_threshold_imu)
        meanErrorCamImu = errorsCamImu.mean() if errorsCamImu.size > 0 else 0
        images.append(image1)

    appendReprojection(args, output, "reprojection", [cameraInd], images, meanErrorCam, meanErrorCamImu)

    for cameraInd0 in range(cameraInd):
        xy = []
        xy0 = []
        for frame in data:
            if frame["camera_ind"] != cameraInd: continue
            frameInd = frame["frame_ind"]
            for i, cornerId in enumerate(frame["corner_ids"]):
                p = detectedDict.get((cameraInd0, frameInd, cornerId))
                if p is None: continue
                xy0.append(p)
                xy.append([frame["detected_px"][i], frame["detected_py"][i]])
        xy0 = np.array(xy0)
        xy = np.array(xy)

        image0 = scatterFrame(args, xy, width, height, f"scatter{cameraInd0}-{cameraInd}", f"Detected {cameraInd0}-{cameraInd} stereo points")
        ret, image1 = bucketCount(args, xy, width, height, f"bucket-stereo{cameraInd0}-{cameraInd}", f"{cameraInd0}-{cameraInd}", args.bucket_full_count_stereo)
        appendCoverage(output, [cameraInd0, cameraInd], [image0, image1], ret, args.coverage_threshold_stereo)

        image0 = scatterFrame(args, xy0, width, height, f"scatter{cameraInd}-{cameraInd0}", f"Detected {cameraInd}-{cameraInd0} stereo points")
        ret, image1 = bucketCount(args, xy0, width, height, f"bucket-stereo{cameraInd}-{cameraInd0}", f"{cameraInd}-{cameraInd0}", args.bucket_full_count_stereo)
        appendCoverage(output, [cameraInd, cameraInd0], [image0, image1], ret, args.coverage_threshold_stereo)

def computeExtrinsicsChecks(args, report_data, calibration, output):
    import numpy as np
    cameraCount = len(calibration["cameras"])
    if cameraCount == 2:
        imuToCam0 = np.array(calibration["cameras"][0]["imuToCamera"])
        imuToCam1 = np.array(calibration["cameras"][1]["imuToCamera"])
        output["vergence_degrees"] = computeVergenceDegrees(imuToCam0, imuToCam1)
        output["baseline_mm"] = 1000 * computeBaseline(imuToCam0, imuToCam1)

    if not "base_calibration" in report_data: return
    baseCalibration = report_data["base_calibration"]
    if len(baseCalibration["cameras"]) != cameraCount:
        print("Base calibration camera count does not match calibration.")
        return

    if cameraCount == 2:
        baseImuToCam0 = np.array(baseCalibration["cameras"][0]["imuToCamera"])
        baseImuToCam1 = np.array(baseCalibration["cameras"][1]["imuToCamera"])
        output["base_calibration_vergence_degrees"] = computeVergenceDegrees(baseImuToCam0, baseImuToCam1)
        output["base_calibration_baseline_mm"] = 1000 * computeBaseline(baseImuToCam0, baseImuToCam1)

    def getImuToCam(calibration, cameraInd):
        return np.array(calibration["cameras"][cameraInd]["imuToCamera"])

    def updatePassed(output, passed):
        if not passed:
            output["extrinsics"]["passed"] = False
            output["passed"] = False

    def angle(R):
        return np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))

    output["extrinsics"] = {
        "passed": True,
        "pairs": [],
    }
    # IMU-to-camera changes.
    for cameraInd in range(cameraCount):
        imuToCam = getImuToCam(calibration, cameraInd)
        baseImuToCam = getImuToCam(baseCalibration, cameraInd)
        camPos = np.linalg.inv(imuToCam)[:3, 3]
        baseCamPos = np.linalg.inv(baseImuToCam)[:3, 3]
        d = np.linalg.norm(camPos - baseCamPos)
        thresholdDist = args.imu_max_rel_position_change * np.linalg.norm(baseCamPos)
        passed = d < thresholdDist
        output["extrinsics"]["pairs"].append({
            "cameraInds": [cameraInd],
            "distance_mm": 1000 * d,
            "threshold_mm": 1000 * thresholdDist,
            "passed": passed,
        })
        updatePassed(output, passed)

        a = angle(imuToCam[:3, :3] @ baseImuToCam[:3, :3].transpose())
        passed = a < args.camera_max_angle_change_degrees
        output["extrinsics"]["pairs"].append({
            "cameraInds": [cameraInd],
            "angle_degrees": a,
            "threshold_degrees": args.camera_max_angle_change_degrees,
            "passed": passed,
        })
        updatePassed(output, passed)

    # Camera-to-camera changes.
    for i1 in range(cameraCount):
        for i0 in range(i1):
            cam1ToCam0 = getImuToCam(calibration, i0) @ np.linalg.inv(getImuToCam(calibration, i1))
            baseCam1ToCam0 = getImuToCam(baseCalibration, i0) @ np.linalg.inv(getImuToCam(baseCalibration, i1))
            cam1Pos = cam1ToCam0[:3, 3]
            baseCam1Pos = baseCam1ToCam0[:3, 3]
            d = np.linalg.norm(cam1Pos - baseCam1Pos)
            thresholdDist = args.camera_max_rel_position_change * np.linalg.norm(baseCam1Pos)
            passed = d < thresholdDist
            output["extrinsics"]["pairs"].append({
                "cameraInds": [i0, i1],
                "distance_mm": 1000 * d,
                "threshold_mm": 1000 * thresholdDist,
                "passed": passed,
            })
            updatePassed(output, passed)

            a = angle(cam1ToCam0[:3, :3] @ baseCam1ToCam0[:3, :3].transpose())
            passed = a < args.camera_max_angle_change_degrees
            output["extrinsics"]["pairs"].append({
                "cameraInds": [i0, i1],
                "angle_degrees": a,
                "threshold_degrees": args.camera_max_angle_change_degrees,
                "passed": passed,
            })
            updatePassed(output, passed)

def generateReport(args, report_data, calibration):
    import numpy as np
    addDefaultsForAdvanced(args)
    width = calibration["cameras"][0]["imageWidth"]
    height = calibration["cameras"][0]["imageHeight"]

    output = { "width": width, "height": height, "passed": True }

    computeExtrinsicsChecks(args, report_data, calibration, output)

    detectedDict = {}
    for frame in report_data["data"]:
        for i, cornerId in enumerate(frame["corner_ids"]):
            detectedDict[(frame["camera_ind"], frame["frame_ind"], cornerId)] = [frame["detected_px"][i], frame["detected_py"][i]]

    for cameraInd in range(len(calibration["cameras"])):
        compute(args, report_data["data"], detectedDict, width, height, cameraInd, output)

    if args.output_json:
        with open(args.output_json, "w") as f:
            f.write(json.dumps(output, indent=4))
        print("Generated JSON report data at:", args.output_json)

    if args.output_html:
        generateHtml(args, report_data, calibration, output, args.output_html)

def report(args, report_data_str):
    report_data = json.loads(report_data_str)
    generateReport(args, report_data["report"], report_data["calibration"])
