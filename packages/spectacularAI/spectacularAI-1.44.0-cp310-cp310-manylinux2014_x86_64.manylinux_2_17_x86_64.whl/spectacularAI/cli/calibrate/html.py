import json

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spectacular AI calibration report</title>
<style>
    .passed { font-weight: bold; color: #008000; }
    .failed { font-weight: bold; color: red; }

    .large-text { font-size: 22px; }

    body {
        font-family: sans-serif;
        max-width: 20cm;
        margin-left: auto;
        margin-right: auto;
        margin-top: 6%;
        margin-bottom: 4%;
        padding-left: 10px;
        padding-right: 10px;
        font-size: 13pt;
    }

    pre {
        font-size: 11pt;
    }

    section {
        margin-bottom: 1.5cm;
    }

    img {
        max-width: 100%;
    }

    table {
        border-collapse: collapse;
    }

    .summary-table td {
        padding-top: 0.25em;
        padding-bottom: 0.25em;
        border-top: 1px solid #cccccc;
        border-bottom: 1px solid #cccccc;
    }

    td.key {
        padding-right: 0.5cm;
        min-width: 5cm;
    }
</style>
</head>
<body>
"""

TAIL = "</body>\n</html>"

def h1(title): return f"<h1>{title}</h1>\n"
def h2(title): return f"<h2>{title}</h2>\n"
def p(text): return f"<p>{text}</p>\n"
def table(pairs):
    s = '<table class="summary-table">\n'
    for key, value in pairs:
        s += '<tr class="summary-row"><td class="key">%s</td><td class="value">%s</td>\n' % (key, value)
    s += "</table>\n"
    return s

def passed(v, large=True):
    if v:
        classes = 'passed'
        text = 'Passed'
    else:
        classes = 'failed'
        text = 'FAILED'
    if large:
        classes +=" large-text"
        tag = 'p'
    else:
        tag = 'span'
    return '<%s class="%s">%s</%s>' % (tag, classes, text, tag)

def generateExtrinsics(args, group):
    s = ""
    s += "<section>\n"
    s += h2("Extrinsics changes to base calibration: {}".format(passed(group["passed"], large=False)))
    for pair in group["pairs"]:
        if pair["passed"]: continue
        if len(pair["cameraInds"]) == 1 and "distance_mm" in pair:
            s += p("Camera #{} position in IMU coordinates changed too much: {:.1f}mm > {:.1f}mm".format(
                pair["cameraInds"][0], pair["distance_mm"], pair["threshold_mm"]))
        elif "distance_mm" in pair:
            s += p("Camera #{} position in Camera #{} coordinates changed too much: {:.1f}mm > {:.1f}mm".format(
                pair["cameraInds"][1], pair["cameraInds"][0], pair["distance_mm"], pair["threshold_mm"]))
        elif len(pair["cameraInds"]) == 1 and "angle_degrees" in pair:
            s += p("Camera #{} angle in IMU coordinates changed too much: {:.1f}&deg > {:.1f}&deg".format(
                pair["cameraInds"][0], pair["angle_degrees"], pair["threshold_degrees"]))
        elif "angle_degrees" in pair:
            s += p("Camera #{} angle in Camera #{} coordinates changed too much: {:.1f}&deg > {:.1f}&deg".format(
                pair["cameraInds"][1], pair["cameraInds"][0], pair["angle_degrees"], pair["threshold_degrees"]))

    if args.verbose_report:
        for pair in group["pairs"]:
            if "distance_mm" in pair:
                s += p("Cameras #{}, distance {:.1f}mm (threshold {:.1f}mm)".format(pair["cameraInds"],
                    pair["distance_mm"], pair["threshold_mm"]))
            elif "angle_degrees" in pair:
                s += p("Cameras #{}, angle {:.1f}&deg (threshold {:.1f}&deg)".format(pair["cameraInds"],
                    pair["angle_degrees"], pair["threshold_degrees"]))
    return s

def generateCoverage(args, group):
    s = ""
    s += "<section>\n"
    passfail = passed(group["passed"], large=False)
    if len(group["cameraInds"]) == 1: s += h2("Coverage in camera #{}: {}".format(group["cameraInds"][0], passfail))
    else: s += h2("Stereo coverage in cameras #{} and #{}: {}".format(group["cameraInds"][0], group["cameraInds"][1], passfail))

    if not group["passed"]:
        s += p("The fraction of white squares in the frame is not high enough: {:.2f} &lt; {:.2f}".format(group["bucketsCoverage"], group["threshold"]))
        if len(group["cameraInds"]) == 1:
            s += p("FOV numbers may be inaccurate.")
    elif args.verbose_report:
        s += p("{:.2f} &gt; {:.2f}".format(group["bucketsCoverage"], group["threshold"]))

    for image in group["images"]:
        s += f'<img src="data:image/png;base64,{image}" alt="Plot">\n'
    s += "</section>\n"
    return s

def generateReprojection(args, group):
    s = ""
    s += "<section>\n"
    s += h2("Reprojection errors in camera #{}: {}".format(group["cameraInds"][0], passed(group["passed"], large=False)))

    if not group["passed"]:
        s += p("Mean reprojection errors are not small enough. Red points have larger errors.")
        if group["errorCam"] >= group["thresholdCam"]:
            s += p("Camera phase: {:.2f} &gt; {:.2f}".format(group["errorCam"], group["thresholdCam"]))
        if group["errorCamImu"] is not None and group["errorCamImu"] >= group["thresholdCamImu"]:
            s += p("Camera-IMU phase: {:.2f} &gt; {:.2f}".format(group["errorCamImu"], group["thresholdCamImu"]))
    elif args.verbose_report:
        s += p("Camera phase: {:.2f} &lt; {:.2f}".format(group["errorCam"], group["thresholdCam"]))
        if group["errorCamImu"] is not None:
            s += p("Camera-IMU phase: {:.2f} &lt; {:.2f}".format(group["errorCamImu"], group["thresholdCamImu"]))

    for image in group["images"]:
        s += f'<img src="data:image/png;base64,{image}" alt="Plot">\n'
    s += "</section>\n"
    return s

def generateHtml(args, data, calibration, output, output_html):
    s = HEAD
    s += h1("Calibration report")
    s += '<section>\n'
    kv_pairs = [
        ('Outcome', passed(output["passed"], large=False)),
        ('Date', data['date']),
        ('Dataset', data["dataset_path"]),
        ('Camera models', data["cam_model"])
    ]
    for i, c in enumerate(data["cameras"]):
        kv_pairs.append((
            'Camera #{} FOV'.format(i),
            "{:.1f}&deg; / {:.1f}&deg; / {:.1f}&deg; (D/H/V)".format(c["dfov_degrees"], c["hfov_degrees"], c["vfov_degrees"])))

    if "baseline_mm" in output:
        v = "{:.0f}mm".format(output["baseline_mm"])
        if "base_calibration_baseline_mm" in output:
            v += " ({:.0f}mm in base calibration)".format(output["base_calibration_baseline_mm"])
        kv_pairs.append(('Baseline', v))
    if "vergence_degrees" in output:
        v = '{:.1f}&deg;'.format(output["vergence_degrees"])
        if "base_calibration_vergence_degrees" in output:
            v += " ({:.1f}&deg in base calibration)".format(output["base_calibration_vergence_degrees"])
        kv_pairs.append(('Vergence', v))
    s += table(kv_pairs)
    if not output["passed"]: s += p("One or more checks below failed.")
    s += '</section>\n'

    if "extrinsics" in output:
        s += generateExtrinsics(args, output["extrinsics"])
    if "reprojection" in output:
        for group in output["reprojection"]:
            s += generateReprojection(args, group)
    if "coverage" in output:
        for group in output["coverage"]:
            s += generateCoverage(args, group)

    s += "<section>\n"
    s += h2("Calibration JSON output")
    s += "<pre>\n"
    s += json.dumps(calibration, indent=4)
    s += "</pre>\n"
    s += "</section>\n"

    s += TAIL

    with open(output_html, "w") as f:
        f.write(s)
    print("Generated HTML report at:", output_html)
