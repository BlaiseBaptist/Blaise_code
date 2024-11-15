#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()

# Robot configuration code
controller_1 = Controller(PRIMARY)
left1 = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
left2 = Motor(Ports.PORT18, GearSetting.RATIO_6_1, False)
left3 = Motor(Ports.PORT15, GearSetting.RATIO_6_1, False)
right1 = Motor(Ports.PORT20, GearSetting.RATIO_6_1, True)
right2 = Motor(Ports.PORT17, GearSetting.RATIO_6_1, True)
right3 = Motor(Ports.PORT14, GearSetting.RATIO_6_1, True)
intake = Motor(Ports.PORT16, GearSetting.RATIO_6_1, True)
left_wing = DigitalOut(brain.three_wire_port.c)
cannon_motor = Motor(Ports.PORT13, GearSetting.RATIO_6_1, False)
right_wing = DigitalOut(brain.three_wire_port.d)


# wait for rotation sensor to fully initialize
wait(30, MSEC)


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")



# define variables used for controlling motors based on controller inputs
controller_1_right_shoulder_control_motors_stopped = True

# define a task that will handle monitoring inputs from controller_1
def rc_auto_loop_function_controller_1():
    global controller_1_right_shoulder_control_motors_stopped, remote_control_code_enabled
    # process the controller input every 20 milliseconds
    # update the motors based on the input values
    while True:
        if remote_control_code_enabled:
            # check the buttonR1/buttonR2 status
            # to control intake
            if controller_1.buttonR1.pressing():
                intake.spin(FORWARD)
                controller_1_right_shoulder_control_motors_stopped = False
            elif controller_1.buttonR2.pressing():
                intake.spin(REVERSE)
                controller_1_right_shoulder_control_motors_stopped = False
            elif not controller_1_right_shoulder_control_motors_stopped:
                intake.stop()
                # set the toggle so that we don't constantly tell the motor to stop when
                # the buttons are released
                controller_1_right_shoulder_control_motors_stopped = True
        # wait before repeating the process
        wait(20, MSEC)

# define variable for remote controller enable/disable
remote_control_code_enabled = True

rc_auto_loop_thread_controller_1 = Thread(rc_auto_loop_function_controller_1)

#endregion VEXcode Generated Robot Configuration
l_group = MotorGroup(left1, left2, left3)
r_group = MotorGroup(right1, right2, right3)
motors = {
    "Left 19": left1,
    "Left 18": left2,
    "Left 15": left3,
    "Right 20": right1,
    "Right 17": right2,
    "Right 14": right3,
    "Intake 16": intake,
    "Cannon 13": cannon_motor,
}
drive_motors = dict(list(motors.items())[0:5])
c1, c2 = Color.RED, Color.BLUE
class cannon:
    def __init__(self, motor, spinning=False, speed=100):
        self.motor_obj = motor
        self.spinning = spinning
        self.speed = speed
    def fire(self, direction):
        if self.spinning:
            self.motor_obj.stop()
            self.spinning = False
            return
        self.motor_obj.spin(direction, self.speed, PERCENT)
        self.spinning = True
def linear_drive(g, t):
    return g + t, g - t
def blaise_drive(ithrottle, iturn):
    left = (blaise_slope(ithrottle)+1) * iturn + ithrottle
    right = (-blaise_slope(ithrottle)-1) * iturn + ithrottle
    return(left,right)
def cal(x):
    return x if abs(x) > 5 else 0
def blaise_slope(x):
    return 0 if x == 0 else x/abs(x) - 0.005*x
def curve(x):
    return (x / 27) ** 3 + x / 2
def driver_loop():
    while True:
        wait(.02, SECONDS)
        drive_code = blaise_drive
        igo, iturn = cal(controller_1.axis3.position()), cal(controller_1.axis1.position())
        Left, Right = drive_code(igo, iturn)
        r_group.spin(FORWARD, Right, PERCENT)
        l_group.spin(FORWARD, Left, PERCENT)

def show_charge():
    while True:
        wait(1,SECONDS)
        controller_1.screen.set_cursor(1,7)
        controller_1.screen.print(pad(brain.battery.capacity(),3) + "%")
def both_wings(state):
    left_wing.set(state)
    right_wing.set(state)
def pad(pct,size):
    out = str(pct)
    return "0"*(size-len(out))+out 
def monitor_temp():
    overheat_temp = 50
    controller_1.screen.clear_screen()
    while True:
        for name, motor_obj in drive_motors.items():
            if motor_obj.temperature() > overheat_temp:
                controller_1.screen.clear_row(2)
                controller_1.screen.clear_row(3)
                controller_1.screen.set_cursor(2,1)
                controller_1.screen.print("OVERHEATED")
                controller_1.screen.set_cursor(3,1)
                controller_1.screen.print(name + " " +str(int(motor_obj.temperature()))+"C")
            while motor_obj.temperature() > overheat_temp:
                l_group.stop()
                r_group.stop()
        wait(1,SECONDS)
def monitor_cannon():
    values = []
    while True:
        if abs(cannon_motor.velocity(PERCENT)) > 98:
            values.append(cannon_motor.power())
            print("watts:", sum(values) / len(values))
            wait(.1, SECONDS)
        else:
            values = []
        if cannon_motor.temperature() > 50:
            cannon_motor.stop()
def monitor_dcs():
    while True:
        dcs = {}
        wait(1, SECONDS)
        for name, motor_obj in motors.items():
            if not motor_obj.installed():
                dcs[name] = motor_obj
        if len(dcs):
            print(" ".join(dcs.keys()))
        else:
            print("No disconnects")
def monitor_drift():
    while True:
        wait(1,SECONDS)
        print(controller_1.axis3.position(),controller_1.axis1.position())
def monitor_time():
    while True:
        wait(1,SECONDS)
        controller_1.screen.set_cursor(1,1)
        ctime = brain.timer.time(SECONDS)
        controller_1.screen.print(pad(int(ctime // 60),2) + ":" + pad(int(ctime % 60),2))
        if abs(ctime) % 15 < 1:
            controller_1.rumble(".")

def set_color(c):
    brain.screen.set_fill_color(c)
    brain.screen.set_pen_color(c)
def draw_half():
    #white screen
    brain.screen.set_fill_color(Color.WHITE)
    brain.screen.draw_rectangle(0,0,480,239)

    #draw net
    brain.screen.set_pen_width(1)
    brain.screen.set_pen_color(Color.RED)
    for x in range(0,80,8):
        for y in range(170,240,8):
            brain.screen.draw_rectangle(x,y,8,8)
    brain.screen.set_pen_color(Color.BLUE)
    for x in range(400,480,8):
        for y in range(170,240,8):
            brain.screen.draw_rectangle(x,y,8,8)

    #draw black goal bars
    brain.screen.set_pen_color(Color.BLACK)
    brain.screen.set_pen_width(3)
    brain.screen.draw_line(80,160,80,240)
    brain.screen.draw_line(400,160,400,240)
    brain.screen.draw_line(480,170,400,170)
    brain.screen.draw_line(0,170,80,170)

    #draw barrier
    brain.screen.set_pen_width(8)
    brain.screen.draw_line(160,80,320,80)
    brain.screen.draw_line(240,80,240,240)

    #draw match load bars
    brain.screen.set_pen_color(Color.BLUE)
    brain.screen.draw_line(80,0,0,80)
    brain.screen.set_pen_color(Color.RED)
    brain.screen.draw_line(400,0,480,80)

    #draw elevation bar
    brain.screen.draw_line(240,0,240,80)

    #draw goal stands
    set_color(Color.BLUE)
    brain.screen.draw_circle(400,160,20)
    set_color(Color.RED)
    brain.screen.draw_circle(80,160,20)
    
    #draw goal bars
    brain.screen.set_pen_color(Color.RED)
    brain.screen.set_pen_width(4)
    brain.screen.draw_line(0,160,80,160)
    brain.screen.set_pen_color(Color.BLUE)
    brain.screen.draw_line(480,160,400,160)
def draw_half2(c1,c2):
    #white screen
    brain.screen.set_fill_color(Color.WHITE)
    brain.screen.draw_rectangle(0,0,480,239)



    #draw barrier
    brain.screen.set_pen_color(Color.BLACK)
    brain.screen.set_pen_width(8)
    brain.screen.draw_line(160,80,320,80)
    brain.screen.draw_line(240,80,240,240)

    #red things
    brain.screen.set_pen_color(c1)
    brain.screen.set_fill_color(Color.TRANSPARENT)
    brain.screen.set_pen_width(1)
    for x in range(0,80,8):
        for y in range(170,240,8):
            brain.screen.draw_rectangle(x,y,8,8)
    brain.screen.set_fill_color(c1)
    brain.screen.set_pen_width(8)
    brain.screen.draw_line(400,0,480,80)
    brain.screen.draw_line(240,0,240,80)
    brain.screen.draw_circle(80,160,20)
    brain.screen.set_pen_width(4)
    brain.screen.draw_line(0,160,80,160)

    #blue things
    brain.screen.set_pen_color(c2)
    brain.screen.set_fill_color(Color.TRANSPARENT)
    brain.screen.set_pen_width(1)
    for x in range(400,480,8):
        for y in range(170,240,8):
            brain.screen.draw_rectangle(x,y,8,8)
    brain.screen.set_fill_color(c2)
    brain.screen.set_pen_width(8)
    brain.screen.draw_line(80,0,0,80)
    brain.screen.draw_circle(400,160,20)
    brain.screen.set_pen_width(4)
    brain.screen.draw_line(480,160,400,160)

    #draw black goal bars
    brain.screen.set_pen_color(Color.BLACK)
    brain.screen.set_pen_width(3)
    brain.screen.draw_line(80,160,80,240)
    brain.screen.draw_line(400,160,400,240)
    brain.screen.draw_line(480,170,400,170)
    brain.screen.draw_line(0,170,80,170)
def offence():
    return True if brain.screen.x_position() > 240 else False
def get_auto():
    global c1,c2
    if brain.screen.y_position() > 200:
        c1, c2 = c2 ,c1
    draw_half2(c1,c2)
    brain.screen.set_pen_width(2)
    brain.screen.set_pen_color(Color.BLACK)
    brain.screen.set_fill_color(Color.TRANSPARENT)
    if offence():
        brain.screen.draw_rectangle(340, 10, 40, 50)

    else:
        brain.screen.draw_rectangle(90,10,40,50)
    brain.screen.draw_circle(brain.screen.x_position(),brain.screen.y_position(),10)
def driver():
    brain.timer.clear()
    Thread(driver_loop)
    Thread(monitor_time)
    left1.set_stopping(COAST)
    right1.set_stopping(COAST)
    left2.set_stopping(BRAKE)
    right2.set_stopping(BRAKE)
    r_group.set_stopping(BRAKE)
    l_group.set_stopping(BRAKE)
    main_cannon = cannon(cannon_motor)
    intake.set_velocity(100,PERCENT)
    controller_1.buttonL1.pressed(lambda: main_cannon.fire(REVERSE))
    controller_1.buttonL2.pressed(lambda: main_cannon.fire(FORWARD))
    controller_1.buttonRight.pressed(lambda: left_wing.set(not (left_wing.value())))
    controller_1.buttonY.pressed(lambda: right_wing.set(not (right_wing.value())))
def spin_time(l,r,t,wt=300):
    l_group.spin(FORWARD,l,PERCENT)
    r_group.spin(FORWARD,r,PERCENT)
    wait(t)
    l_group.stop()
    r_group.stop()
    wait(wt)
def auto():
    intake.spin(FORWARD,-100,PERCENT)
    l_group.set_stopping(HOLD)
    r_group.set_stopping(HOLD)
    if offence():
        spin_time(-30,30,270) 
        left_wing.set(True)
        spin_time(30,20,800)
        left_wing.set(False)
        spin_time(-45,-15,700)
        spin_time(-30,-30,1050)
    else:
        spin_time(30,10,900,wt=3)
        spin_time(30,30,100)
        spin_time(15,35,700)
        spin_time(25,35,700)
        spin_time(-30,-30,1000)
#mcan = Thread(monitor_cannon)
#mdc = Thread(monitor_dcs)
#mdf = Thread(monitor_drift)
temps = Thread(monitor_temp)
charge = Thread(show_charge)

draw_half2(c1,c2)
brain.screen.pressed(get_auto)

competition = Competition(driver, auto)
