module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  const mockData = {
    status: "Running",
    tasksCompletedToday: 42,
    totalPointsEarned: 1250,
    recentActivity: [
      { id: 1, time: "10:45 AM", action: "Completed survey on freecash.com", reward: "+150 pts" },
      { id: 2, time: "10:30 AM", action: "Completed offer on lootably.com", reward: "+300 pts" },
      { id: 3, time: "10:15 AM", action: "Logged in to surveytime.io", reward: "Status OK" },
      { id: 4, time: "10:00 AM", action: "Auto-payout executed on Cointiply", reward: "$3.50 BTC" },
      { id: 5, time: "09:45 AM", action: "Cleared cookies and rotated proxy", reward: "Success" }
    ]
  };

  res.status(200).json(mockData);
};
