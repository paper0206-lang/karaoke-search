export default async function handler(req, res) {
  // 設定CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  try {
    return res.status(200).json({
      success: true,
      message: 'API測試成功',
      timestamp: new Date().toISOString(),
      method: req.method,
      query: req.query
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}