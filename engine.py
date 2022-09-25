import cv2
import numpy as np

def order_points(pts):
    '''
    pts: list of (x,y) coordinates
    returns: ordered points clock wise
    top-left, top-right, bottom-right, bottom-left
    '''
    final = sorted(pts, key=lambda k: [k[0], k[1]])
    final[-1], final[-2] = final[-2], final[-1]
    return final


def mask_image(points_list, image):
    '''
    points_list: list of np.ndarry of points 
    returns: masked image around the points
    '''
    if points_list is not None:
        mask = np.zeros(image.shape[:2], np.uint8)
        for points in points_list:
            if points is not None:
                cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)
            else:
                continue
        _masked_img = cv2.bitwise_and(image, image, mask=mask)
        return _masked_img
    else:
        return image


def get_bbox_points(corners):
    '''
    get the bounding box points, tl and br from corners of detected whiteboard
    '''
    pts = np.array(corners,dtype="int32")
    x = pts[:,0]
    y = pts[:,1]
    return (min(x),min(y)), (max(x),max(y))


def detect_whiteboard(img, debug=False):
    '''
    img: raw image with one or more white boards
    returns: list of white boards detected
    '''
    # Blank canvas.
    con = np.zeros_like(img)
    # Resize image to workable size
    dim_limit = 1080
    max_dim = max(img.shape)
    if max_dim > dim_limit:
        resize_scale = dim_limit / max_dim
        img = cv2.resize(img, None, fx=resize_scale, fy=resize_scale)
    # Create a copy of resized original image for later use
    orig_img = img.copy()
    # Repeated Closing operation to remove text from the document.
    kernel = np.ones((5, 5), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=3)
    # GrabCut
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (20, 20, img.shape[1] - 20, img.shape[0] - 20)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img = img * mask2[:, :, np.newaxis]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)
    # Edge Detection.
    canny = cv2.Canny(gray, 0, 200)
    canny = cv2.dilate(canny, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

    # Finding contours for the detected edges.
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Keeping only the largest detected contour.
    # page = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    # sorting the contours
    page = sorted(contours, key=cv2.contourArea, reverse=True)

    # Detecting Edges through Contour approximation.
    # Loop over the contours.
    boards_con = []
    if len(page) == 0:
        return [], orig_img
    for c in page:
        # Approximate the contour.
        epsilon = 0.02 * cv2.arcLength(c, True)
        corners = cv2.approxPolyDP(c, epsilon, True)
        # If our approximated contour has four points.
        if len(corners) == 4:
            boards_con.append(corners)
    
    board_crops = []
    for corners in boards_con:
        # Sorting the corners and converting them to desired shape.
        corners = sorted(np.concatenate(corners).tolist())
        con = cv2.drawContours(con, page, -1, (0, 255, 255), 3)
        if debug:
            print("whiteboard corners: ",corners)

        # For 4 corner points being detected.
        corners = order_points(np.array(corners))
        if debug:
            print("ordered corners: ",corners)
        
        # Displaying the corners.
        for index, c in enumerate(corners):
            character = chr(65 + index)
            cv2.putText(con, character, tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2, cv2.LINE_AA)
        if debug:
            cv2.imshow("contours",con)
            cv2.waitKey(0)

        final = mask_image([np.array(corners)],orig_img)
        if debug:
            cv2.imshow("masked",final)
            cv2.waitKey(0)

        pt1, pt2 = get_bbox_points(corners)
        if (pt2[0]-pt1[0]) > 150:
            if debug:
                print("corners: ", corners)
                print("pts: ",pt1, pt2)
            cv2.rectangle(orig_img, pt1, pt2, (0,0,255), 2)
            board_crops.append(final)
    if debug:
        cv2.imshow("final",orig_img)
        cv2.waitKey(0)
    
    # if len(board_crops) > 1 :
    #     board_crops = np.concatenate(board_crops, axis=0)
    # else:
    #     board_crops = board_crops[0]
    return board_crops, orig_img

def init_text_detector():
    import easyocr
    reader = easyocr.Reader(['en'])
    return reader

def detect_text(images, reader):
    results = []
    for img in images:
        res = reader.readtext(img, paragraph=True)
        results.append(res[0][-1])
    results = list(set(results))
    results = ' '.join(results)
    return results


if __name__ == '__main__':
    import time
    print("Time taken for 1 image for:")

    img = cv2.imread("static/sample/sample5.jpeg")

    since = time.time()
    boards, fimgs = detect_whiteboard(img, debug=False)
    print(f"detection: {time.time()- since}")

    reader = init_text_detector()
    since = time.time()
    print(detect_text(boards, reader))
    print(f"text: {time.time()- since}")
