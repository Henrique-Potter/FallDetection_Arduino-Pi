
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.stage.Stage;

public class FaDe extends Application {

    private Text textCounter;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        Button btn = new Button();
        btn.setText("Start Fall Detection Service");
        btn.setOnAction((ActionEvent event) -> {
            startScheduledExecutorService();
        });

        textCounter = new Text();
        Text textCounter2 = new Text();
        textCounter.setFont(Font.font("Verdana", 20));
        textCounter.setFill(Color.RED);

        VBox vBox = new VBox();
        vBox.getChildren().addAll(btn, textCounter2,textCounter);
        vBox.setAlignment(Pos.CENTER);
        vBox.setPadding(new Insets(10, 10, 10, 10));

        StackPane root = new StackPane();
        root.getChildren().addAll(vBox);
        root.setAlignment(Pos.CENTER);

        Scene scene = new Scene(root, 300, 250);

        primaryStage.setTitle("FaDe - Fall Detection Alarm");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private void startScheduledExecutorService() {

        final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

        scheduler.scheduleAtFixedRate(new Runnable() {
            int counter = 0;

            @Override
            public void run() {
                counter++;

                Platform.runLater(() -> {
                    try {
                        String response = update();
                        //String response = "asd asd asd asds 1";
                        textCounter.setText("No Alarms :"
                                + "\n"
                                + "Request Count: "
                                + String.valueOf(counter) + " ");

                        String data[] = response.split(" ");
                        if (!data[4].equals("0")) {
                            textCounter.setFont(Font.font("Verdana", 20));
                            textCounter.setFill(Color.RED);
                            textCounter.setText("Alarm!!!");
                        } else {
                            textCounter.setFont(Font.font("Verdana", 14));
                            textCounter.setFill(Color.BLACK);
                        }

                    } catch (Exception ex) {
                        System.out.println("");
                        Logger.getLogger(FaDe.class.getName()).log(Level.SEVERE, null, ex);
                        return;
                    }
                });

            }
        },
                1,
                2,
                TimeUnit.SECONDS);
    }

    private String update() throws Exception {

        String uri = "http://192.168.240.1/arduino/digital/3";
        URL url = new URL(uri);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        connection.setRequestProperty("Accept", "application/json");

        connection.setConnectTimeout(5000);
        connection.setReadTimeout(5000);

        BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        String line;
        StringBuilder response = new StringBuilder();

        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();
        connection.disconnect();
        return response.toString();
    }

}
