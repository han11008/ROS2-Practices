#include <chrono> // for std::chrono::duration
#include <memory> // for std::make_shared
#include <functional> // for std::bind
#include <string> // for std::to_string
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class talker : public rclcpp::Node
{
public:
	talker() : Node("talker_node")
	{
		publisher = create_publisher<std_msgs::msg::String>("greeting", 10);
		count = 0;
		timer = create_wall_timer(std::chrono::milliseconds(750),
					std::bind(&talker::timer_callback, this));
	}

private:
	rclcpp::TimerBase::SharedPtr timer;
	rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher;
	int count;

	void timer_callback()
	{
		auto msg = std_msgs::msg::String();
		msg.data = std::to_string(count++) + ": Hello!";
		RCLCPP_INFO(get_logger(), "Publishing: [%s]", msg.data.c_str());
		publisher->publish(msg);
	}
};

int main(int argc, char **argv)
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<talker>());
	rclcpp::shutdown();
	return 0;
}
