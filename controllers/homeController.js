//Be able to run python program
const { spawn } = require('child_process');

exports.respondHome = (req, res) => {
  res.render("home");
};

exports.respondAbout = (req, res) => {
  res.render("about");
};

exports.respondBlackLitterman = (req, res) => {
  res.render("blacklitterman");
};

exports.respondContact = (req, res) => {
  res.render("contact");
};

exports.respondBLWeights = (req, res) => {
  const tickers = (req.body.tickers).toUpperCase().trim().split(",");
  const expected = (req.body.expected).trim().split(",");
  const confidences = (req.body.confidences).trim().split(",");
  let weights = [];

  let args = ['PyPortfolioOpt.py'];
  args.push(tickers, expected, confidences);

  const childProcess = spawn('python', args);

  childProcess.stdout.setEncoding('utf8');
  childProcess.stdout.on('data', (data) => {
      // only last data recieved saved (final calculations)
      weights = data;
      console.log(`Node output: ${data}`);
  })

  childProcess.stderr.setEncoding('utf8');
  childProcess.stderr.on('data', (err) => {
      console.error(err);
  })

  childProcess.on('exit', () => {
      console.log('The python script has exited');
      res.render("bl-weights", {"weights": weights});
  })
};
