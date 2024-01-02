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

exports.respondBLForm = (req, res) => {
  const tickers = ((req.body.tickers).replaceAll(" ", "")).toUpperCase();
  const expected = (req.body.expected).replaceAll(" ", "");
  const confidences = (req.body.confidences).replaceAll(" ", "");
  let dataIn = [];

  // run python script of black litterman algorithm
  let args = ['BlackLittermanAlgorithm.py'];
  args.push(tickers, expected, confidences);

  const childProcess = spawn('python', args);

  // on output recieved from script
  childProcess.stdout.setEncoding('utf8');
  childProcess.stdout.on('data', (data) => {
    // only last data recieved saved (final calculations)
    dataIn = data;
    console.log(`Node output: ${data}`);
  })

  // if error occurs
  childProcess.stderr.setEncoding('utf8');
  childProcess.stderr.on('data', (err) => {
    console.error(err);
  })

  // when script ends
  childProcess.on('exit', () => {
    console.log('The python script has exited');
    // format output to display
    weights = dataIn.split(" ");
    weights.splice(0, 1);
    weights.splice(weights.length - 1, 1);

    res.render("bl-form", {"tickers": tickers.split(","), "weights": weights});
  })
};
