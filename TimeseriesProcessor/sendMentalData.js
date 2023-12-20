const Influx = require("influx");

// InfluxDB configuration
const influx = new Influx.InfluxDB({
  host: "localhost",
  port: "8086",
  protocol: "http",
  database: "mindflow",
});

const data = require("C:\\Resources\\SIH\\MindFlow_Backend\\MindFlow_BackEnd\\TimeseriesProcessor\\data.json");

// Define InfluxDB measurement
const measurement = "mental_health_data";

// Map data to InfluxDB points
const points = data.map((item) => ({
  measurement,
  tags: { name: item.Name },
  fields: {
    timestamp: item.Timestamp,
    mentalStatePrediction: item.MentalStatePrediction,
    suicideRiskAssessment: item.SuicideRiskAssessment,
  },
}));

// Write data to InfluxDB
influx
  .writePoints(points)
  .then(() => console.log("Data written to InfluxDB successfully"))
  .catch((err) => console.error(`Error writing to InfluxDB: ${err.message}`));
