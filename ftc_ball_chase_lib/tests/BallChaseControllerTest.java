/*
 * BallChaseControllerTest - TeleOp harness for the no-odometry
 * BallChaseController tool. Use this to validate everything before trusting it
 * in auto:
 *
 *   Right bumper (HOLD) : run the chase. Releasing it aborts instantly and
 *                         returns manual control.
 *   D-pad in init       : pick which ball classes to chase (UP = red,
 *                         DOWN = blue, LEFT = red+blue default, RIGHT = all).
 *   Left stick / right stick X : manual drive.  Left bumper : intake.
 *
 * The auto equivalent is just this loop body: create the controller, start(),
 * update() each loop until isDone(), abort() when done.
 */
package org.firstinspires.ftc.teamcode;

import com.qualcomm.hardware.limelightvision.Limelight3A;
import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;
import org.junit.jupiter.api.Disabled;

/** Robot-side harness, not part of the deployed core: lives in tests/ and is
 *  @Disabled so it never shows up in a match-ready build. */
@Disabled("robot-only interactive harness")
@TeleOp(name = "Ball Chase Tool Test", group = "Hive Vision")
public class BallChaseControllerTest extends LinearOpMode {

    @Override
    public void runOpMode() {
        DcMotor lf = hardwareMap.get(DcMotor.class, HiveConfig.MOTOR_LEFT_FRONT);
        DcMotor rf = hardwareMap.get(DcMotor.class, HiveConfig.MOTOR_RIGHT_FRONT);
        DcMotor lb = hardwareMap.get(DcMotor.class, HiveConfig.MOTOR_LEFT_BACK);
        DcMotor rb = hardwareMap.get(DcMotor.class, HiveConfig.MOTOR_RIGHT_BACK);
        DcMotor intake = hardwareMap.tryGet(DcMotor.class, HiveConfig.MOTOR_INTAKE);   // optional

        BallChaseController.configureMecanumDirections(lf, rf, lb, rb);
        for (DcMotor m : new DcMotor[]{lf, rf, lb, rb}) {
            m.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
            m.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        }

        Limelight3A limelight = hardwareMap.get(Limelight3A.class, HiveConfig.LIMELIGHT_NAME);
        limelight.pipelineSwitch(HiveConfig.LIMELIGHT_PIPELINE);
        limelight.setPollRateHz(HiveConfig.LIMELIGHT_POLL_RATE_HZ);
        limelight.start();

        BallTracker tracker = new BallTracker(limelight);
        BallChaseController chase = new BallChaseController(tracker, lf, rf, lb, rb, intake);
        chase.setMaxPickups(3);

        while (!isStarted() && !isStopRequested()) {
            if (gamepad1.dpad_up)    tracker.setAllowedClasses(BallTracker.CLASS_RED);
            if (gamepad1.dpad_down)  tracker.setAllowedClasses(BallTracker.CLASS_BLUE);
            if (gamepad1.dpad_left)  tracker.setAllowedClasses(BallTracker.CLASSES_RED_BLUE);
            if (gamepad1.dpad_right) tracker.setAllowedClasses(BallTracker.CLASSES_ALL);

            telemetry.addLine("Hold RIGHT BUMPER to chase; release = manual.");
            telemetry.addLine("Init: UP=red DOWN=blue LEFT=red+blue RIGHT=all");
            telemetry.addData("chasing", BallTracker.class.getSimpleName()
                    + " classes: " + tracker.getAllowedClasses());
            telemetry.update();
        }

        waitForStart();

        boolean wasHeld = false;
        while (opModeIsActive()) {
            boolean held = gamepad1.right_bumper;
            if (held && !wasHeld) chase.start();
            if (!held && wasHeld) chase.abort();
            wasHeld = held;

            if (held) {
                chase.update();
            } else {
                lf.setPower(-gamepad1.left_stick_y + gamepad1.left_stick_x
                        + gamepad1.right_stick_x);
                rf.setPower(-gamepad1.left_stick_y - gamepad1.left_stick_x
                        - gamepad1.right_stick_x);
                lb.setPower(-gamepad1.left_stick_y - gamepad1.left_stick_x
                        + gamepad1.right_stick_x);
                rb.setPower(-gamepad1.left_stick_y + gamepad1.left_stick_x
                        - gamepad1.right_stick_x);
                if (intake != null) intake.setPower(gamepad1.left_bumper ? 1.0 : 0.0);
            }

            chase.addTelemetry(telemetry);
            telemetry.update();
        }

        chase.abort();
        limelight.stop();
    }
}