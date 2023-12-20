const Influx = require("influx");

// InfluxDB configuration
const influx = new Influx.InfluxDB({
  host: "localhost",
  port: "8086",
  protocol: "http",
  database: "mindflow",
});

const data = require("C:\\Resources\\SIH\\MindFlow_Backend\\MindFlow_BackEnd\\TimeseriesProcessor\\femaleData.json");

// Define InfluxDB measurement
const measurement = "female_health_data";

// Map data to InfluxDB points
const points = data.map((item) => ({
  measurement,
  tags: { name: item.Name },
  fields: {
    timestamp: item.Timestamp,
    nextPeriodDate: item["Next Period Date"],
    ageGroup: item["Age group"],
    threat_date: item["Threat Level (Date)"],
    threat_flow: item["Threat Level (Flow)"],
    threat_moodSwing: item["Threat Level (Mood Swing)"],
    threat_health: item["Threat Level (Health)"],
    threat_dateDifference: item["Date Difference (Days)"],
    threat_totalThreat: item["Total Threat"],
  },
}));

// Write data to InfluxDB
influx
  .writePoints(points)
  .then(() => console.log("Data written to InfluxDB successfully"))
  .catch((err) => console.error(`Error writing to InfluxDB: ${err.message}`));
