let currentState = {
  status: "Idle",
  tasksCompleted: 0,
  pointsEarned: 0,
  recentActivity: []
};

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method === 'GET') {
    return res.status(200).json(currentState);
  }

  if (req.method === 'POST') {
    const apiKey = process.env.STATUS_API_KEY;
    if (apiKey) {
      const clientKey = req.headers['x-api-key'];
      if (clientKey !== apiKey) {
        return res.status(401).json({ error: 'Unauthorized' });
      }
    }

    const { status, tasksCompleted, pointsEarned, activity } = req.body || {};

    if (status) currentState.status = status;
    if (typeof tasksCompleted === 'number') currentState.tasksCompleted = tasksCompleted;
    if (typeof pointsEarned === 'number') currentState.pointsEarned = pointsEarned;

    if (activity) {
      currentState.recentActivity.unshift(activity);
      if (currentState.recentActivity.length > 5) {
        currentState.recentActivity = currentState.recentActivity.slice(0, 5);
      }
    }

    return res.status(200).json({ success: true, state: currentState });
  }

  return res.status(405).json({ error: 'Method Not Allowed' });
};
