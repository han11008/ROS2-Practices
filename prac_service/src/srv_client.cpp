#include <memory> // for std::shared_ptr
#include <chrono> // for std::chrono::duration
#include <functional> // for std::bind
#include <thread> // for std::this_thread::sleep_for
#include <cstdlib> // for std::rand
#include "rclcpp/rclcpp.hpp"
#include "custom_interfaces/srv/add_three_ints.hpp"

class sumClient : public rclcpp::Node
{
public:
	sumClient() : Node("client_node")
	{
		client = create_client<custom_interfaces::srv::AddThreeInts>("add_three_ints");
		send_request();
	}
private:
	rclcpp::Client<custom_interfaces::srv::AddThreeInts>::SharedPtr client;
	
	void send_request()
	{
		while(rclcpp::ok()) {
			while (!client->wait_for_service(std::chrono::seconds(1))) {
				if (!rclcpp::ok()) {
					RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Interrupted while waiting for server");
					return;
				}
				RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Waiting for server to be available...");
			}
			auto request = std::make_shared<custom_interfaces::srv::AddThreeInts::Request>();
			request->a = (int64_t)std::rand() % 100;
			request->b = (int64_t)std::rand() % 100;
			request->c = (int64_t)std::rand() % 100;
			RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Sending request of summing: a=%ld, b=%ld, c=%ld", request->a, request->b, request->c);
			auto response = client->async_send_request(request);
			if (rclcpp::spin_until_future_complete(this->get_node_base_interface(), response) == rclcpp::FutureReturnCode::SUCCESS) {
				auto result = response.get();
				RCLCPP_INFO(rclcpp::get_logger("rclcpp"), "Getting result: sum=%ld", result->sum);
			}
			else {
				RCLCPP_ERROR(rclcpp::get_logger("rclcpp"), "Failed getting result");
			}
			std::this_thread::sleep_for(std::chrono::seconds(3));
		}
	}
};

int main(int argc, char **argv)
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<sumClient>());
	rclcpp::shutdown();
	return 0;
}
