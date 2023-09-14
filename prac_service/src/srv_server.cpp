#include <memory> //for std::shared_ptr
#include <functional> // for std::bind
#include "rclcpp/rclcpp.hpp"
#include "custom_interfaces/srv/add_three_ints.hpp"

class sumServer : public rclcpp::Node
{
public:
	sumServer() : Node("server_node")
	{
		server = create_service<custom_interfaces::srv::AddThreeInts>("add_three_ints", std::bind(&sumServer::add, this, std::placeholders::_1, std::placeholders::_2));
    }
	
private:
	rclcpp::Service<custom_interfaces::srv::AddThreeInts>::SharedPtr server;
	
	void add(const std::shared_ptr<custom_interfaces::srv::AddThreeInts::Request> request, std::shared_ptr<custom_interfaces::srv::AddThreeInts::Response> response)
	{
		response->sum = request->a + request->b + request->c;
		RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Request of summing: a=%ld, b=%ld, c=%ld", request->a, request->b, request->c);
		RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Response the result: sum=%ld", response->sum);
	}
};

int main(int argc, char **argv)
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<sumServer>());
	rclcpp::shutdown();
	return 0;
}
