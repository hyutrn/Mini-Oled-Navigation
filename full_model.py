import os
import cv2
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from ultralytics import YOLO


label_descriptions = {
    "102": "Cấm ngược chiều",
    "103a": "Cấm xe ôtô",
    "103b": "Cấm ôtô rẻ phải",
    "103c": "Cấm ôtô rẻ trái",
    "117": "Hạn chế chiều cao",
    "123a": "Cấm rẻ trái",
    "123b": "Cấm rẻ phải",
    "124a": "Cấm quay đầu",
    "124c": "Cấm rẻ trái quay đầu",
    "127_40": "Tốc độ tối đa 40km/h",
    "127_60": "Tốc độ tối đa 60km/h",
    "127_70": "Tốc độ tối đa 70km/h",
    "127_80": "Tốc độ tối đa 80km/h",
    "128": "Cấm bóp còi",
    "130": "Cấm dừng và đổ",
    "131a": "Cấm đổ",
    "131b": "Cấm đổ lẻ",
    "136": "Cấm đi thẳng",
    "137": "Cấm rẻ trái và phải",
    "201a": "Chổ ngoặt nguy hiểm trái",
    "203a": "Đường hẹp",
    "205a": "Giao nhau cùng cấp",
    "207a": "Giao nhau không ưu tiên",
    "208": "Giao nhau ưu tiên",
    "221": "Đường không bằng phẳng",
    "227": "Công trường",
    "239a": "Cáp điện phía trên",
    "244": "Đi chậm",
    "301": "Đi thẳng",
    "302": "Đi sang phải",
    "303": "Vòng xuyến",
    "401": "Bắt đầu đường ưu tiên",
    "402": "Hết ưu tiên",
    "423": "Đường đi bộ",
    "425": "Bệnh viện",
    "434": "Bến xe buýt",
    "111b_111d": "Cấm xe 3 bánh và xe 4 bánh thô sơ",
    "409": "Được phép quay đầu",
    "118": "Hạn chế chiều ngang",
    "217": "Đường hầm",
    "403b": "Đường giành cho ôtô và môtô",
    "306_30": "Tốc độ tối thiếu là 30km/h",
    "121": "Cự ly tối thiếu",
    "125": "Cấm vượt",
    "307_30": "Hết hạn chế tốc độ tối thiểu",
    "236": "Hết đường đôi",
    "204": "Đường hai chiều",
    "241": "Đoạn đường hay xảy ra tai nạn",
    "301e": "Chỉ được rẻ trái",
    "301d": "Chỉ được rẻ phải",
    "407a": "Đường một chiều",
    "218": "Cửa chui",
    "124b": "Cấm ôtô quay đầu",
    "201b": "Chổ ngoặt nguy hiểm phải",
    "202": "Nhiều chổ ngoặt",
    "203b": "Đường hẹp trái",
    "204c": "Đường hẹp phải",
    "207b": "Giao nhau không ưu tiên",
    "205b": "Giao nhau đồng cấp",
    "205d": "Giao nhau đồng cấp",
    "205e": "Giao nhau đồng cấp",
    "207c": "Giao nhau không ưu tiên",
    "133": "Hết cấm vượt",
    "135": "Hết lệnh cấm",
    "238": "Tốc độ tối đa là 90km/h",
    "127_100": "Tốc độ tối đa là 100km/h",
    "403a": "Đường dành cho ôtô",
    "437": "Đường cao tốc",
    "101": "Đường cấm",
    "405c": "Đường cụt",
    "129": "Trạm thuế",
    "408": "Nơi đậu xe",
    "306_60": "Tốc độ tối thiếu là 60km/h",
    "219": "Dốc xuống",
    "220": "Dốc lên",
    "239b": "Chiều cao an toàn",
    }

def get_exif_data(image_path):
    """
    Trích xuất toàn bộ dữ liệu EXIF từ ảnh.
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            print(f"Không có dữ liệu EXIF trong ảnh {image_path}.")
            return None
        return {TAGS.get(key): value for key, value in exif_data.items() if key in TAGS}
    except Exception as e:
        print(f"Lỗi khi lấy EXIF từ ảnh {image_path}: {e}")
        return None


def get_gps_info(exif_data):
    """
    Trích xuất thông tin GPS từ EXIF.
    """
    if not exif_data:
        return {"GPS_Latitude": "None", "GPS_Longitude": "None"}

    gps_info = exif_data.get("GPSInfo")
    if not gps_info:
        print("Không tìm thấy thông tin GPS trong EXIF.")
        return {"GPS_Latitude": "None", "GPS_Longitude": "None"}

    gps_data = {GPSTAGS.get(key): value for key, value in gps_info.items() if key in GPSTAGS}

    def convert_to_degrees(value):
        """
        Convert tọa độ từ (degrees, minutes, seconds) sang độ thập phân.
        """
        if len(value) == 3:
            d, m, s = value
        elif len(value) == 2:
            d, m = value
            s = 0
        else:
            return None
        return d + (m / 60.0) + (s / 3600.0)

    latitude = None
    longitude = None

    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
        lat = gps_data["GPSLatitude"]
        lat_ref = gps_data["GPSLatitudeRef"]
        latitude = convert_to_degrees(lat)
        if lat_ref != "N":
            latitude = -latitude

    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
        lon = gps_data["GPSLongitude"]
        lon_ref = gps_data["GPSLongitudeRef"]
        longitude = convert_to_degrees(lon)
        if lon_ref != "E":
            longitude = -longitude

    if latitude is None or longitude is None:
        print(f"Lỗi khi trích xuất tọa độ GPS từ EXIF: {gps_data}")

    return {
        "GPS_Latitude": latitude if latitude is not None else "None",
        "GPS_Longitude": longitude if longitude is not None else "None",
    }


def process_input(model, source_path, output_image_folder=None, output_excel_path=None, is_video=False):
    """
    Hàm xử lý cả video và ảnh, trích xuất kết quả bounding box, nhãn và GPS.
    """
    data = []  # Danh sách chứa kết quả

    # Nếu là video
    if is_video:
        cap = cv2.VideoCapture(source_path)
        if not cap.isOpened():
            print(f"Không thể mở video: {source_path}")
            return

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break  # Kết thúc video

            frame_count += 1
            print(f"Đang xử lý khung hình {frame_count}...")

            # Dự đoán trên khung hình
            try:
                results = model.predict(source=frame, conf=0.25, save=False, show=False)
                print(f"Số lượng bounding box phát hiện được: {len(results[0].boxes)}")
            except Exception as e:
                print(f"Lỗi khi dự đoán khung hình {frame_count}: {e}")
                continue

            # Lấy thông tin GPS từ EXIF (nếu có)
            gps_info = None
            if frame_count == 1:  # Chỉ lấy GPS của khung hình đầu tiên
                exif_data = get_exif_data(source_path)
                gps_info = get_gps_info(exif_data)
                print(f"Thông tin GPS: {gps_info}")

            for result in results:
                if result.boxes:  # Kiểm tra nếu có bounding boxes
                    for box in result.boxes:
                        try:
                            label = model.names[int(box.cls[0])] if box.cls else "None"
                            confidence = box.conf[0].item() if box.conf else "None"

                            # Lấy thông tin GPS từ EXIF (nếu có)
                            gps_data = {
                                "Label": label if label else "None",
                                "Confidence": confidence if confidence else "None",
                                "Description": label_descriptions.get(label, "Không có mô tả"),
                            }

                            # Thêm thông tin GPS (nếu có)
                            if gps_info:
                                gps_data.update(gps_info)
                            else:
                                gps_data.update({"GPS_Latitude": "None", "GPS_Longitude": "None"})

                            # Lưu dữ liệu vào data
                            data.append(gps_data)

                            # Hiển thị thông tin trích xuất ra terminal
                            print(f"Frame {frame_count} - Label: {label}, Confidence: {confidence}, GPS_Latitude: {gps_data.get('GPS_Latitude', 'None')}, GPS_Longitude: {gps_data.get('GPS_Longitude', 'None')}")
                        except Exception as e:
                            print(f"Lỗi khi xử lý bounding box: {e}")

        cap.release()

    # Nếu là ảnh
    else:
        if os.path.isdir(source_path):  # Nếu là thư mục ảnh
            os.makedirs(output_image_folder, exist_ok=True)
            image_files = [os.path.join(source_path, f) for f in os.listdir(source_path) if
                           f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"Số lượng ảnh tìm thấy trong thư mục: {len(image_files)}")

            for image_path in image_files:
                print(f"Đang xử lý ảnh: {image_path}")
                results = model.predict(source=image_path, conf=0.1, save=False)

                # Trích xuất thông tin EXIF và GPS (nếu có)
                exif_data = get_exif_data(image_path)
                gps_info = get_gps_info(exif_data) if exif_data else {"GPS_Latitude": "None", "GPS_Longitude": "None"}
                print(f"Thông tin GPS từ EXIF: {gps_info}")

                for result in results:
                    print(f"Số lượng bounding box phát hiện được: {len(result.boxes)}")
                    # Lưu kết quả vào thư mục
                    output_image_path = os.path.join(output_image_folder, os.path.basename(image_path))
                    annotated_image = result.plot()
                    cv2.imwrite(output_image_path, annotated_image)

                    if result.boxes:
                        for box in result.boxes:
                            try:
                                label = model.names[int(box.cls[0])] if box.cls else "None"
                                confidence = box.conf[0].item() if box.conf else "None"

                                # Thêm thông tin GPS vào kết quả
                                gps_data = {
                                    "Label": label if label else "None",
                                    "Confidence": confidence if confidence else "None",
                                    "Description": label_descriptions.get(label, "Không có mô tả"),
                                }

                                # Thêm GPS vào dữ liệu nếu có
                                gps_data.update(gps_info)

                                # Lưu dữ liệu vào data
                                data.append(gps_data)

                                # Hiển thị thông tin trích xuất ra terminal
                                print(f"Image: {image_path} - Label: {label}, Confidence: {confidence}, GPS_Latitude: {gps_data.get('GPS_Latitude', 'None')}, GPS_Longitude: {gps_data.get('GPS_Longitude', 'None')}")
                            except Exception as e:
                                print(f"Lỗi khi xử lý bounding box: {e}")

        else:  # Nếu chỉ là một ảnh duy nhất
            image_path = source_path
            print(f"Đang xử lý ảnh: {image_path}")
            results = model.predict(source=image_path, conf=0.1, save=False)

            # Trích xuất thông tin EXIF và GPS (nếu có)
            exif_data = get_exif_data(image_path)
            gps_info = get_gps_info(exif_data) if exif_data else {"GPS_Latitude": "None", "GPS_Longitude": "None"}
            print(f"Thông tin GPS từ EXIF: {gps_info}")

            for result in results:
                # Lưu kết quả vào thư mục
                output_image_path = os.path.join(output_image_folder, os.path.basename(image_path))
                annotated_image = result.plot()
                cv2.imwrite(output_image_path, annotated_image)

                if result.boxes:
                    for box in result.boxes:
                        try:
                            label = model.names[int(box.cls[0])] if box.cls else "None"
                            confidence = box.conf[0].item() if box.conf else "None"

                            # Thêm thông tin GPS vào kết quả
                            gps_data = {
                                "Label": label if label else "None",
                                "Confidence": confidence if confidence else "None",
                                "Description": label_descriptions.get(label, "Không có mô tả"),
                            }

                            # Thêm GPS vào dữ liệu nếu có
                            gps_data.update(gps_info)

                            # Lưu dữ liệu vào data
                            data.append(gps_data)

                            # Hiển thị thông tin trích xuất ra terminal
                            print(f"Image: {image_path} - Label: {label}, Confidence: {confidence}, GPS_Latitude: {gps_data.get('GPS_Latitude', 'None')}, GPS_Longitude: {gps_data.get('GPS_Longitude', 'None')}")
                        except Exception as e:
                            print(f"Lỗi khi xử lý bounding box: {e}")

    # Lưu kết quả vào Excel
    gps_data["Description"] = label_descriptions.get(label, "Không có mô tả")

    if output_excel_path:
        os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)

        # Lọc bỏ nhãn "car"
        filtered_data = [row for row in data if row["Label"].lower() != "car"]

        # Chuyển danh sách thành DataFrame (không có "Confidence")
        df = pd.DataFrame(filtered_data, columns=["Label", "GPS_Latitude", "GPS_Longitude", "Description"])

        if len(filtered_data) > 0:
            df.to_excel(output_excel_path, index=False, engine='openpyxl')
            print(f"Kết quả chi tiết đã lưu tại: {output_excel_path}")
        else:
            print("Không có dữ liệu hợp lệ để lưu vào Excel.")


# ---------------------
# Chạy chương trình

# Đường dẫn đầu vào (ảnh hoặc video)
input_path = r"C:\Users\User\Desktop\DO_AN\ảnh test\Test\Test"  # Hoặc video
output_image_folder = r"C:\Users\User\Desktop\DO_AN\output_images"  # Thư mục lưu ảnh kết quả
output_excel_path = r"C:\Users\User\Desktop\DO_AN\output_results.xlsx"  # Đường dẫn lưu Excel

# Tải mô hình YOLO
model_path = r"C:\Users\User\Desktop\DO_AN\train_xongg\last.pt"
model = YOLO(model_path)

# Kiểm tra loại tệp trong thư mục đầu vào
if os.path.isdir(input_path):
    # Nếu là thư mục, kiểm tra xem có video hay ảnh không
    video_files = [f for f in os.listdir(input_path) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
    image_files = [f for f in os.listdir(input_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if video_files:
        input_type = 'video'
    elif image_files:
        input_type = 'image'
    else:
        print("Không có video hoặc ảnh trong thư mục.")
        exit()
else:
    # Nếu là file ảnh hoặc video duy nhất
    input_type = 'video' if input_path.lower().endswith(('.mp4', '.avi', '.mov')) else 'image'

# Xử lý đầu vào
if input_type == 'image':
    process_input(model, input_path, output_image_folder=output_image_folder, output_excel_path=output_excel_path,
                  is_video=False)
elif input_type == 'video':
    process_input(model, input_path, output_image_folder=None, output_excel_path=output_excel_path, is_video=True)
else:
    print("Không hỗ trợ loại tệp này!")
