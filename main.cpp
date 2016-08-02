#include <iostream>
#include <ctime>
#include <string>
#include <sstream>
#include <fstream>

#include <limbo/limbo.hpp>
#include <opencv2/opencv.hpp>
#include <boost/format.hpp>

#include "tensegrity-controller.hpp"
#include "tracker.hpp"
#include "serial.hpp"

using namespace limbo;

//#define MAXSPEED 254
#define USE_LIBCMAES 1

struct Params {
    // option for the Bayesian optimizer
    struct bayes_opt_boptimizer {
        BO_PARAM(double, noise, 0.5);
        BO_PARAM(int,hp_period,-1);
    };

    struct stat_gp{
      BO_PARAM(int,bins,50);
    };
    // enable / disable the output
    struct bayes_opt_bobase {
      BO_PARAM(int, stats_enabled, true);
    };

    // options for the internal optimizer
    #ifdef USE_LIBCMAES
    struct opt_cmaes : public defaults::opt_cmaes { };
    // std::cout << "Using LIBCMAES" << std::endl;
    #elif defined(USE_NLOPT)
    struct opt_nloptnograd : public defaults::opt_nloptnograd { };
    #else
    struct opt_gridsearch : public defaults::opt_gridsearch { };
    #endif

    // options for the initializer
    struct init_randomsampling {
        //BO_PARAM(int, samples, 10);
        BO_PARAM(int, samples, 10);
    };

    // options for the stopping criteria
    struct stop_maxiterations {
        BO_PARAM(int, iterations, 40);
    };
    struct kernel_exp
    {
      // how big the neighborhood is, from [0,1]
      BO_PARAM(double, sigma_sq, 0.15);
      BO_PARAM(double, l, 1.0);
    };

    struct mean_constant {
            ///@ingroup mean_defaults
            // the higher the value, relative to the
            // actual behavior, the more optimistic we are

            //JB says - keep it around average of random trials
            BO_PARAM(double, constant, 0.05);
        };

    struct acqui_ucb {
      /// @ingroup acqui_defaults
      // exploit --> smaller values
      // explore --> bigger values
      // (scaled relative to performance of Eval)
      BO_PARAM(double, alpha, 0.2);
        };

    // options for the hyper-parameter optimizer
    // (here we just take the default values)
    struct opt_rprop : public defaults::opt_rprop { };
    struct opt_parallelrepeater : public defaults::opt_parallelrepeater { };
};


namespace global
{
  std::string serialPort("/dev/ttyUSB0");
  Observer eye(0, true);
  std::string outDirName;
}

struct Eval {
    static constexpr size_t dim_in = 3;
    static constexpr size_t dim_out = 1;

    Eigen::VectorXd operator()(const Eigen::VectorXd& x) const
    {
        //Create the tensegrity controller
        tensegrity::Tensegrity_Controller tens(global::serialPort);

        // Create output file name prefix
        std::stringstream outFilePrefixStream;
        outFilePrefixStream << x(0) << "_" << x(1) << "_" << x(2);

        std::string outVidFilename = global::outDirName + "/" + outFilePrefixStream.str() + "_VIDEO.avi";
        std::string outTextFilename = global::outDirName + "/" + outFilePrefixStream.str() + "_DATA.txt";

        // Create the video output
        int codec = CV_FOURCC('M', 'J', 'P', 'G');
        Size frameSize = global::eye.getFrameSize();

        VideoWriter outputVideo;
        outputVideo.open(outVidFilename, codec, 15.0, frameSize);
        if (!outputVideo.isOpened())
        {
          std::cout << "Could not open the output video for write: " << outVidFilename << std::endl;
          exit(-2);
        }

        // Create the data output and formatter
        std::ofstream outputText;
        outputText.open(outTextFilename);
        boost::format outDataFormatter("| X: %1$=+10d | Y: %2$=+10d | Theta: %3$=+10d \n");
        outputText << "Motor 1: " << x(0) << " Motor 2: " << x(1) << " Motor 3: " << x(2) << std::endl;

        bool retry = 0;

        Eigen::VectorXd res(1);

        //std::string str;
        //std::cout<<"press any key then enter to start" << std::endl;
        //std::cin >> str;

		    //Deprecated, can get rid of
        int MAX_TRIALS = 1;

        std::vector<double> distances;
        for (int trials = 0; trials < MAX_TRIALS; trials++)
        {

        do {
          retry = 0;
        std::cout << x.transpose() << std::endl;
        // we have determined that negative motor values produce
        // distinct behaviors from postive ones in some cases
        // and so have expanded the range of values accordingly.

        float originAngle, curAngle, endingAngle;
        Point2f originLoc, curLoc, endingLoc;

        namedWindow("Tracking Preview");

        global::eye.clearFrame();
        global::eye.updateLocationInfo();
        originLoc = global::eye.getCenter();
        originAngle = global::eye.getAngle();

        // Print out the origin location and angle
        std::cout << "Origin location: X: " << originLoc.x << " Y: " << originLoc.y << std::endl;
        std::cout << "Origin angle: " << originAngle << std::endl;

        // Make sure we actually have a valid origin location and angle
        while (originLoc.x != originLoc.x) {
          global::eye.updateLocationInfo();
          originLoc = global::eye.getCenter();
          originAngle = global::eye.getAngle();
          std::cout << "Origin location: X: " << originLoc.x << " Y: " << originLoc.y << std::endl;
          std::cout << "Origin angle: " << originAngle << std::endl;
        }

        outDataFormatter % originLoc.x;
        outDataFormatter % originLoc.y;
        outDataFormatter % originAngle;
        outputText << outDataFormatter;

        tens.set_all_motor_speeds(x(0)*2*MAXSPEED-MAXSPEED,
                                  x(1)*2*MAXSPEED-MAXSPEED,
                                  x(2)*2*MAXSPEED-MAXSPEED);

        usleep(19990);
        //
        // tens.set_motor_speed(0,x(0)*254-127);
        // tens.set_motor_speed(1,x(1)*254-127);
        // tens.set_motor_speed(2,x(2)*254-127);
        //
 //       std::cout<<" now we are waiting!"<<std::endl;
        int elapsed = 0;
        int sleeptime = 10000;
        int evaltime =  1000000;
        float yawmax = 1.0;


        int strikes = 0;
        int maxStrikes = 3;

		//Yaw is rotation on y-axis (up)
        double roll = 0;
        double pitch = 0;
        double yaw = 0;

        while (elapsed < evaltime)
        {
          global::eye.updateLocationInfo();
          curLoc = global::eye.getCenter();
          curAngle = global::eye.getAngle();

          outDataFormatter % curLoc.x;
          outDataFormatter % curLoc.y;
          outDataFormatter % curAngle;
          outputText << outDataFormatter;

          Mat frame;
          frame = global::eye.getFrame();
          if(frame.empty()) {
            std::cout << "Empty frame!" << std::endl;
            continue;
          }
          circle(frame, curLoc, 5, Scalar(10,10,10), -1);
          line(frame, curLoc, Point2f( curLoc.x + (50 * cos(curAngle)), curLoc.y + (50 * sin(curAngle))), Scalar( 25, 25, 25 ), 3 );
          outputVideo << frame;
          imshow("Tracking Preview", frame);

          if(waitKey(1)!= -1)
          {
          destroyWindow("Final Image");
                break;
          };

          usleep(sleeptime);
          elapsed += sleeptime;
          if (fabs(curAngle - originAngle) > yawmax)
          {
            std::cout << yaw << "is over limit, strike #" <<strikes << std::endl;
            strikes++;
          }
          else{
            strikes--;
            strikes = std::max(strikes,0);
          }
          if (strikes > maxStrikes)
          {
            std::cout << yaw << " is past yaw limit, bailing after " << strikes << " strikes" << std::endl;
            break;
          }
          // std::cout << "Angle change: " << (curAngle - originAngle) * (180/3.14159) << std::endl;


        }
        // std::cout << "Delta RPY: " << roll << " " << pitch << " " << yaw << std::endl;
        tens.stop_all_motors();

        global::eye.updateLocationInfo();
        endingLoc = global::eye.getCenter();
        endingAngle = global::eye.getAngle();

        // Print final location
        std::cout << "Ending location: X: " << endingLoc.x << " Y: " << endingLoc.y << std::endl;

        //Make sur we have a valid final location
        while (endingLoc.x != endingLoc.x) {
          global::eye.updateLocationInfo();
          endingLoc = global::eye.getCenter();
          std::cout << "Ending location: X: " << endingLoc.x << " Y: " << endingLoc.y << std::endl;
        }

        outDataFormatter % endingLoc.x;
        outDataFormatter % endingLoc.y;
        outDataFormatter % endingAngle;
        outputText << outDataFormatter;

        // Eigen::Vector3d end = tracker::GetPosition();
        //  Eigen::Vector3d end = global::pos.pos;
        //  t.GetPosition();

        double xDist = endingLoc.x - originLoc.x;
        double yDist = endingLoc.y - originLoc.y;

        double d = sqrt((xDist * xDist) + (yDist * yDist));
        //std::cout<<"new position:"<<pos.pos.transpose()<<std::endl;
        std::cout<<" distance:" << d << std::endl;
        outputText << "Distance: " << d;
        outputText.close();

        res(0) = d;

        std::string str;
        std::cout<<"Press y to restart, x to zero value, any other key to continue" << std::endl;
        std::cin >> str;
        if (str == "y")
          retry = 1;
        else if (str == "x")
        {
          d = 0;
          res(0) = d;
        }

      }while (retry == 1);

      distances.push_back(res(0));

}
      double min_distance = *std::max_element(distances.begin(), distances.end());
      std::cout<<"Distances:";
      for (auto x : distances)
        std::cout<<x<< " ";
      std::cout<<std::endl;
      res(0) = min_distance;
      return res;
  }
};

#include <Eigen/Core>

namespace limbo {
    namespace mean {
        ///@ingroup mean
        ///Use the mean of the observation as a constant mean
        template <typename Params>
        struct Prior {
          typedef kernel::Exp<Params> kf_t;
          typedef mean::Constant<Params> mean_t;
          typedef model::GP<Params, kf_t, mean_t> model_t;
          typedef model::GP<Params, kf_t, mean_t, model::gp::KernelLFOpt<Params>> GP_t;

            Prior(int dim_out=1) : _gp(3, 1) {
              for (int i = 0; i < 2; ++i)
                for (int j = 0; j < 2; ++j)
                  for (int k = 0; k < 2; ++k)
                  {
                    Eigen::VectorXd v(3);
                    v << i, j, k;
                    auto o = tools::make_vector(0.3);
                    _gp.add_sample(v, o, 0.05);
                  }
              Eigen::VectorXd v(3);
              v << 0.5, 0.5, 0.5;
              auto o = tools::make_vector(0);
              _gp.add_sample(v,o,0.05);
            }

            template <typename GP>
            Eigen::VectorXd operator()(const Eigen::VectorXd& v, const GP& gp) const
            {
                return _gp.mu(v);
            }
          protected:
            model_t _gp;
        };
    }
}


int main(int argc, char** argv) {
  srand(time(0));
  int opt;
  while ((opt = getopt(argc, argv, "pc:")) != -1) {
    switch (opt) {
      case 'p':
      std::cout << "using port " << optarg << std::endl;
      global::serialPort = std::string(optarg);
      break;
      // case 'c':
      // std::cout << "using camera " << optarg << std::endl;
      // global::eye = Observer((int)optarg[0]-48, true);
      // global::eye.getNewPuffVals();
      // break;
      default: /* '?' */
      fprintf(stderr, "Usage: %s [-p port]\n",
      argv[0]);
      exit(EXIT_FAILURE);
    }
  }

  // Configure motor controllers
  // char* __;
  // serial::Serial serial_port(global::serialPort,B19200);
  // std::cout << "Configure first motor controller...";
  // std::cin.ignore();
  // std::string conf_str(7,0);
  // conf_str[0] = 0xAA;
  // conf_str[1] = 0x09;
  // conf_str[2] = 0x04;
  // conf_str[3] = 0x00;
  // conf_str[4] = 0x02;
  // conf_str[5] = 0x55;
  // conf_str[6] = 0x2A;
  // conf_str[7] = 0x00;
  // serial_port.send(conf_str);
  //
  // std::cout << "Configure second motor controller...";
  // std::cin.ignore();
  // conf_str[0] = 0xAA;
  // conf_str[1] = 0x09;
  // conf_str[2] = 0x04;
  // conf_str[3] = 0x00;
  // conf_str[4] = 0x03;
  // conf_str[5] = 0x55;
  // conf_str[6] = 0x2A;
  // conf_str[7] = 0x00;
  // serial_port.send(conf_str);

  using stat_t =
  boost::fusion::vector<stat::ConsoleSummary<Params>,
  stat::Samples<Params>,
  stat::Observations<Params>,
  stat::GP<Params> >;

  typedef kernel::Exp<Params> kf_t;

  // CHANGE THIS
  // TOP IS NO PRIOR
  // typedef mean::Constant<Params> mean_t;
  typedef mean::Prior<Params> mean_t;

  // typedef model::GP<Params, kf_t, mean_t> GP_t;

  typedef model::GP<Params, kf_t, mean_t > model_t;
  typedef acqui::UCB<Params, model_t> acqui_t;

  // Create output folder
  time_t t = time(0);
  struct tm * now = localtime( & t );
  std::stringstream outputDirectoryName;
  outputDirectoryName << "/home/james/Desktop/limbo/build/exp/voltaire/TEST_"
                      << (now->tm_year + 1900) << '-'
                      << (now->tm_mon + 1) << '-'
                      <<  now->tm_mday << "-"
                      << now->tm_hour << ":"
                      << now->tm_min;

  global::outDirName = outputDirectoryName.str();
  boost::filesystem::path dir(global::outDirName);
  if(boost::filesystem::create_directory(dir)) {
    std::cout << "Created new directory!" << "\n";
  }

  //CHANGE THIS
  //TOP IS NO PRIOR
  bayes_opt::BOptimizer<Params, statsfun<stat_t>,modelfun<model_t>, acquifun<acqui_t>> boptimizer;
  // bayes_opt::BOptimizer<Params, statsfun<stat_t>, initfun<limbo::init::RandomSampling<Params>>, acquifun<acqui_t>> boptimizer;
  boptimizer.optimize(Eval());
  std::cout << "Best sample: " << boptimizer.best_sample() << " - Best observation: " << boptimizer.best_observation()(0) << std::endl;
  return 0;

}
