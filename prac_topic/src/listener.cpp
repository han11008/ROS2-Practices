#include <memory>  // for std::make_shared
#include <functional> // for std::bind
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class listener : public rclcpp::Node
{
public:
	listener() : Node("listener_node")
	{
		subscriber = create_subscription<std_msgs::msg::String>("greeting", 10,
						std::bind(&listener::callback, this, std::placeholders::_1));
	}

private:
	rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscriber;

	void callback(const std_msgs::msg::String::SharedPtr msg)
	{
		RCLCPP_INFO(get_logger(), "Hearing: [%s]", msg->data.c_str());
	}
};

int main(int argc, char **argv)
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<listener>());
	rclcpp::shutdown();
	return 0;
}
