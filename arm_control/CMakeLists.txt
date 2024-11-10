cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(pico-projects)

pico_sdk_init()

add_executable(main main.c src/Servo.c)

target_include_directories(main PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(main pico_stdlib hardware_pwm hardware_gpio hardware_adc)

pico_enable_stdio_usb(main 1)
pico_enable_stdio_uart(main 0)

pico_add_extra_outputs(main)
