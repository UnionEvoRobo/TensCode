#include <stdio.h>
#include <cmath>
#include <opencv2/opencv.hpp>

#include "tracker.hpp"

bool DEBUG = false;
bool GET_PUFFS = false;

using namespace cv;

void change_thresh(int, void*) {}

Mat threshold_image(Mat src,
                    int hueLow, int hueHigh,
                    int satLow, int satHigh,
                    int valLow, int valHigh) {
  /**
  Function to take in an image and some threshold values and then output a
  binary image in which the pixels withing the threshold are white (255,255,255)
  and those outside the threshold are black (0,0,0).

  Written by James Boggs
  Latest Update: 6/30/2016
  */
  // Setup temporary images
  Mat blurval, threshed;

  // Blur and use the inRange function to threshold the image.
  blur( src, blurval, Size(1, 1));
  inRange(
    blurval,
    Scalar(hueLow, satLow, valLow),
    Scalar(hueHigh, satHigh, valHigh),
    threshed);
  return threshed;
}

Point2f find_puff_center(Mat threshed) {
  /**
  Function which takes in a binary thresholded image and finds the center of the
  first blob it sees. In this context there should only be one blob, the puff
  ball we're tracking.

  Written by James Boggs
  Last updated 7/6/16
  */
  //Find the contours (of which there should only be one)
  std::vector<std::vector<Point> > contours;
  std::vector<Vec4i> hierarchy;
  findContours( threshed, contours, hierarchy, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE );

  // Find the moments of the contours
  Moments mu;
  if (contours.size() > 0) {
    mu = moments( contours[0], false );
  } else {
    return Point2f(nan(""), nan(""));
  }

  // Get the centers
  Point2f center = Point2f( mu.m10/mu.m00 , mu.m01/mu.m00 );

  return center;
}

std::vector<Point2f> find_puff_centers(Mat red_threshed, Mat green_threshed, Mat blue_threshed) {
  /**
  Function which takes in three binary images and returns an ordered vector with
  four elements. Each element of the vector lists the center of one of the puff
  balls or the center of the tensegrity itself. The order of the vector is:
  centers[0] = red center
  centers[1] = green center
  centers[2] = blue center
  centers[3] = all center

  Written by James Boggs
  Last updated 6.30.2016
  */
  // Find the center of each image
  Point2f red_center = find_puff_center(red_threshed);
  Point2f green_center = find_puff_center(green_threshed);
  Point2f blue_center = find_puff_center(blue_threshed);
  Point2f all_center((red_center.x + green_center.x + blue_center.x)/3, (red_center.y + green_center.y + blue_center.y)/3);

  //Put the centers into the vector and return it
  std::vector<Point2f> centers(4);
  centers[0] = red_center;
  centers[1] = green_center;
  centers[2] = blue_center;
  centers[3] = all_center;
  return centers;
}

int* get_puff_vals(VideoCapture cap, int* puff_vals) {
  int hueHigh = 255;
  int satHigh = 255;
  int valHigh = 255;
  int hueLow = 0;
  int satLow = 0;
  int valLow = 0;

  bool cont = true;
  int keyPress = 0;

  bool DEBUG = true;

  namedWindow( "Control Panel", CV_WINDOW_AUTOSIZE );
  namedWindow( "Final Image", CV_WINDOW_AUTOSIZE );
  if (DEBUG) {
    namedWindow( "DEBUG", CV_WINDOW_AUTOSIZE );
  }

  createTrackbar( "Hue High: ",
                "Control Panel", &hueHigh,
                255, change_thresh );
  createTrackbar( "Sat. High: ",
                "Control Panel", &satHigh,
                255, change_thresh );
  createTrackbar( "Val. High: ",
                "Control Panel", &valHigh,
                255, change_thresh );

  createTrackbar( "Hue Low: ",
                "Control Panel", &hueLow,
                255, change_thresh );
  createTrackbar( "Sat. Low: ",
                "Control Panel", &satLow,
                255, change_thresh );
  createTrackbar( "Val. Low: ",
                "Control Panel", &valLow,
                255, change_thresh );

  while (cont)
  {
    Mat frame, converted, threshed, pre_final, final;

    // Capture frame, convert to HSV, filter it, and convert back
    cap >> frame;
    if (frame.empty()) {
      std::cout << "Empty original frame!" << std::endl;
      continue;
    }
    cvtColor(frame, converted, CV_BGR2HSV);
    if (converted.empty()) {
      std::cout << "Empty converted frame" << std::endl;
      continue;
    }
    threshed = threshold_image(converted,
                    hueLow, hueHigh,
                    satLow, satHigh,
                    valLow, valHigh);
    if (threshed.empty()) {
      std::cout << "Empty thresholded frame" << std::endl;
      continue;
    }
    bitwise_and(frame, frame, pre_final, threshed);
    final = pre_final.clone();


    if( final.empty() ) break;
    imshow("Final Image", final);
    if (DEBUG) {
      imshow( "DEBUG", threshed);
    };
    if(waitKey(1)!= -1) //Press any key to exit
    {
      destroyWindow("Final Image");
      destroyWindow("DEBUG");
      destroyWindow("Control Panel");
      cont = false;
    };
  }
  puff_vals[0] = hueHigh;
  puff_vals[1] = satHigh;
  puff_vals[2] = valHigh;
  puff_vals[3] = hueLow;
  puff_vals[4] = satLow;
  puff_vals[5] = valLow;
}

float get_abs_angle(Point2f tens_center, Point2f reference) {
  /**
  Get the absolute angle of the tensegrity fro the upper left corner.
  */
  Point2f horizontal(0, tens_center.y);
  float tens_to_horiz_len = sqrt(pow(tens_center.x - horizontal.x, 2) +
                                 pow(tens_center.y - horizontal.y, 2));

  float tens_to_ref_len = sqrt(pow(tens_center.x - reference.x, 2) +
                               pow(tens_center.y - reference.y, 2));

  float horiz_to_ref_len = sqrt(pow(horizontal.x - reference.x, 2) +
                                pow(horizontal.y - reference.y, 2));

  float angle = acos(
                  (pow(tens_to_horiz_len, 2) +
                  pow(tens_to_ref_len, 2) -
                  pow(horiz_to_ref_len, 2)) /
                  (2*tens_to_horiz_len*tens_to_ref_len)
                );

  return angle;
}

Observer::Observer( int camNum, bool GET_PUFFS ) {
  try
  {
    if(!cap.open(camNum))
    {
      throw -1;
    }
  } catch ( int e ) {
    std::cout << "Could not open the camera number " << camNum << std::endl;
  }

  if (GET_PUFFS) {

    // Get and indicate the threshold boundaries for each puff ball
    std::cout << "Choose red puff ball values..." << std::endl;
    get_puff_vals(cap, red_puff_vals);

    std::cout << "Choose green puff ball values..." << std::endl;
    get_puff_vals(cap, green_puff_vals);

    std::cout << "Choose blue puff ball values..." << std::endl;
    get_puff_vals(cap, blue_puff_vals);

    printf( "Red Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
        red_puff_vals[3], red_puff_vals[0],
        red_puff_vals[4], red_puff_vals[1],
        red_puff_vals[5], red_puff_vals[2]);
    printf( "Green Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
        green_puff_vals[3], green_puff_vals[0],
        green_puff_vals[4], green_puff_vals[1],
        green_puff_vals[5], green_puff_vals[2]);
    printf( "Blue Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
        blue_puff_vals[3], blue_puff_vals[0],
        blue_puff_vals[4], blue_puff_vals[1],
        blue_puff_vals[5], blue_puff_vals[2]);
  } else {
    red_puff_vals[0] = 10;
    red_puff_vals[1] = 255;
    red_puff_vals[2] = 255;
    red_puff_vals[3] = 0;
    red_puff_vals[4] = 174;
    red_puff_vals[5] = 50;
    green_puff_vals[0] = 85;
    green_puff_vals[1] = 255;
    green_puff_vals[2] = 255;
    green_puff_vals[3] = 70;
    green_puff_vals[4] = 140;
    green_puff_vals[5] = 60;
    blue_puff_vals[0] = 115;
    blue_puff_vals[1] = 255;
    blue_puff_vals[2] = 255;
    blue_puff_vals[3] = 100;
    blue_puff_vals[4] = 170;
    blue_puff_vals[5] = 110;
  }
}

bool Observer::isHome() {
  Size frameSize = getFrameSize();
  Point2f vidCenter( frameSize.width / 2, frameSize.height / 2 );
  float tensDisplacement = sqrt( abs( (center.x - vidCenter.x) * (center.x - vidCenter.x) + (center.y - vidCenter.y) * (center.y - vidCenter.y) ) );
  std::cout << "Tens is " << tensDisplacement << " units from the center." << std::endl;
  return ( tensDisplacement <= 50);
}

void Observer::getNewPuffVals() {
  std::cout << "Choose red puff ball values..." << std::endl;
  get_puff_vals(cap, red_puff_vals);

  std::cout << "Choose green puff ball values..." << std::endl;
  get_puff_vals(cap, green_puff_vals);

  std::cout << "Choose blue puff ball values..." << std::endl;
  get_puff_vals(cap, blue_puff_vals);

  printf( "Red Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
      red_puff_vals[3], red_puff_vals[0],
      red_puff_vals[4], red_puff_vals[1],
      red_puff_vals[5], red_puff_vals[2]);
  printf( "Green Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
      green_puff_vals[3], green_puff_vals[0],
      green_puff_vals[4], green_puff_vals[1],
      green_puff_vals[5], green_puff_vals[2]);
  printf( "Blue Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
      blue_puff_vals[3], blue_puff_vals[0],
      blue_puff_vals[4], blue_puff_vals[1],
      blue_puff_vals[5], blue_puff_vals[2]);
}

void Observer::clearFrame() {
  for (int i = 0; i < 10; i++) {
    cap >> curFrame;
  }
}

void Observer::updateLocationInfo() {
  // Create empty images
  Mat frame, converted, tracking;
  Mat red_threshed, green_threshed, blue_threshed;

  // Capture frame and convert to HSV
  cap >> frame;
  if (frame.empty()) {
    std::cout << "Empty original frame!" << std::endl;
    return;
  }
  cvtColor(frame, converted, CV_BGR2HSV);
  if (converted.empty()) {
    std::cout << "Empty converted frame" << std::endl;
    return;
  }

  // get the thresholded image for each puff ball
  red_threshed = threshold_image(converted,
      red_puff_vals[3], red_puff_vals[0],
      red_puff_vals[4], red_puff_vals[1],
      red_puff_vals[5], red_puff_vals[2]);

  green_threshed = threshold_image(converted,
      green_puff_vals[3], green_puff_vals[0],
      green_puff_vals[4], green_puff_vals[1],
      green_puff_vals[5], green_puff_vals[2]);

  blue_threshed = threshold_image(converted,
      blue_puff_vals[3], blue_puff_vals[0],
      blue_puff_vals[4], blue_puff_vals[1],
      blue_puff_vals[5], blue_puff_vals[2]);

  bool DEBUG = false;
  if (DEBUG) {
    namedWindow("RED DEBUG");
    namedWindow("GREEN DEBUG");
    namedWindow("BLUE DEBUG");
    imshow("DEBUG: RED", red_threshed);
    imshow("DEBUG: GREEN", green_threshed);
    imshow("DEBUG: BLUE", blue_threshed);
  }
  if(waitKey(1)!= -1) //Press any key to exit
  {
    if(DEBUG) {
      destroyWindow("RED DEBUG");
      destroyWindow("GREEN DEBUG");
      destroyWindow("BLUE DEBUG");
    }
  };

  // Get the center of the tensegrity and its angle
  std::vector<Point2f> centers = find_puff_centers(red_threshed, green_threshed, blue_threshed);
  Observer::abs_angle = (get_abs_angle(centers[3], centers[0]));
  if (centers[3].y < centers[0].y) {
    abs_angle * -1;
  }
  center = centers[3];
  curFrame = frame.clone();
}

Point2f Observer::getCenter() {  return center; }

float Observer::getAngle() { return abs_angle; }

Mat Observer::getFrame() { return curFrame; }

int Observer::getCodec() { return static_cast<int>(cap.get(CV_CAP_PROP_FOURCC)); }

Size Observer::getFrameSize() { return Size((int) cap.get(CV_CAP_PROP_FRAME_WIDTH),
                                            (int) cap.get(CV_CAP_PROP_FRAME_HEIGHT)
                                        );
                              }

// int main(int argc, char* argv[]) {
//   // Some basic setup
//   int camNum = 0;
//
//   if(argc > 1)
//   {
//     camNum = argv[1][0] - 48;
//   }
//
  // VideoCapture cap;
  // if(!cap.open(camNum))
  // {
  //   return 0;
  // }
//
  // int red_puff_vals[6];
  // int green_puff_vals[6];
  // int blue_puff_vals[6];
//
  // if (GET_PUFFS) {
  //   // Get and indicate the threshold boundaries for each puff ball
  //   std::cout << "Choose red puff ball values..." << std::endl;
  //   get_puff_vals(cap, red_puff_vals);
  //
  //   std::cout << "Choose green puff ball values..." << std::endl;
  //   get_puff_vals(cap, green_puff_vals);
  //
  //   std::cout << "Choose blue puff ball values..." << std::endl;
  //   get_puff_vals(cap, blue_puff_vals);
  //
  //   printf( "Red Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
  //       red_puff_vals[3], red_puff_vals[0],
  //       red_puff_vals[4], red_puff_vals[1],
  //       red_puff_vals[5], red_puff_vals[2]);
  //   printf( "Green Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
  //       green_puff_vals[3], green_puff_vals[0],
  //       green_puff_vals[4], green_puff_vals[1],
  //       green_puff_vals[5], green_puff_vals[2]);
  //   printf( "Blue Puff Values:\n  H: %u to %u\n  S: %u to %u\n, V: %u to %u\n",
  //       blue_puff_vals[3], blue_puff_vals[0],
  //       blue_puff_vals[4], blue_puff_vals[1],
  //       blue_puff_vals[5], blue_puff_vals[2]);
  // } else {
  //   red_puff_vals[0] = 10;
  //   red_puff_vals[1] = 255;
  //   red_puff_vals[2] = 255;
  //   red_puff_vals[3] = 0;
  //   red_puff_vals[4] = 174;
  //   red_puff_vals[5] = 50;
  //   green_puff_vals[0] = 85;
  //   green_puff_vals[1] = 255;
  //   green_puff_vals[2] = 255;
  //   green_puff_vals[3] = 70;
  //   green_puff_vals[4] = 140;
  //   green_puff_vals[5] = 60;
  //   blue_puff_vals[0] = 115;
  //   blue_puff_vals[1] = 255;
  //   blue_puff_vals[2] = 255;
  //   blue_puff_vals[3] = 100;
  //   blue_puff_vals[4] = 170;
  //   blue_puff_vals[5] = 110;
  // }
//
//
//   // Display tracking
//   Mat frame, converted, tracking;
//   Mat red_threshed, green_threshed, blue_threshed;
//   namedWindow("Tracking Display", CV_WINDOW_AUTOSIZE);
//   if (DEBUG) {
//     namedWindow("DEBUG: RED", CV_WINDOW_AUTOSIZE);
//     namedWindow("DEBUG: GREEN", CV_WINDOW_AUTOSIZE);
//     namedWindow("DEBUG: BLUE", CV_WINDOW_AUTOSIZE);
//   }
//   while (true) {
//     // get each frame and convert it to HSV
//     cap >> frame;
//     tracking = frame.clone();
//     cvtColor(frame, converted, CV_BGR2HSV);
//
//     // get the thresholded image for each puff ball
//     red_threshed = threshold_image(converted,
//         red_puff_vals[3], red_puff_vals[0],
//         red_puff_vals[4], red_puff_vals[1],
//         red_puff_vals[5], red_puff_vals[2]);
//
//     green_threshed = threshold_image(converted,
//         green_puff_vals[3], green_puff_vals[0],
//         green_puff_vals[4], green_puff_vals[1],
//         green_puff_vals[5], green_puff_vals[2]);
//
//     blue_threshed = threshold_image(converted,
//         blue_puff_vals[3], blue_puff_vals[0],
//         blue_puff_vals[4], blue_puff_vals[1],
//         blue_puff_vals[5], blue_puff_vals[2]);
//
//     // get the centers for each puff ball, and the geometric center
//     std::vector<Point2f> centers = find_puff_centers(red_threshed, green_threshed, blue_threshed);
//     float angle = (get_abs_angle(centers[3], centers[0]));
//     if (centers[3].y < centers[0].y) {
//       angle = angle * -1;
//     }
//
//     // draw circles
//     circle(tracking, centers[0], 5, Scalar(10,10,255), -1);
//     circle(tracking, centers[1], 5, Scalar(10,255,10), -1);
//     circle(tracking, centers[2], 5, Scalar(255,10,10), -1);
//     circle(tracking, centers[3], 5, Scalar(10,10,10), -1);
//
//     if (centers[3] != centers[3]) {
//       continue;
//     }
//
//     // draw angle lines
//     Point2f horizontal(0, centers[3].y);
//     line(tracking, centers[3], horizontal, Scalar(10,10,10), 3);
//     Point2f angle_ref((cos(angle)*-50) + centers[3].x, (sin(angle)*-50) + centers[3].y);
//     line(tracking, centers[3], angle_ref, Scalar(150,150,150), 3);
//     // line(tracking, centers[3], centers[0], Scalar(255,255,10), 3);
//
//     //print locations
//     printf("Center: %f, %f | Angle: %f\n", centers[3].x, centers[3].y, angle * 57.2958);
//
//     imshow("Tracking Display", tracking);
//     if (DEBUG) {
//       imshow("DEBUG: RED", red_threshed);
//       imshow("DEBUG: GREEN", green_threshed);
//       imshow("DEBUG: BLUE", blue_threshed);
//     }
//     if(waitKey(1)!= -1) //Press any key to exit
//     {
//       destroyWindow("Final Image");
//       break;
//     };
//   }
//
//   return 0;
// }
