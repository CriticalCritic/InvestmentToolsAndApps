// be able to run python program
const { spawn } = require('child_process');

exports.respondHome = (req, res) => {
  res.render("home", {"active": "home"});
};

exports.respondAbout = (req, res) => {
  res.render("about", {"active": "about"});
};

exports.respondBlackLitterman = (req, res) => {
  res.render("blacklitterman", {"active": "bl"});
};

exports.respondRandomForestClassifier = (req, res) => {
  res.render("randomforestclassifier", {"active": "rfc"});
}

exports.respondContact = (req, res) => {
  res.render("contact", {"active": "contact"});
};

// Black Litterman form submission
exports.respondBLForm = (req, res) => {
  const tickers = ((req.body.tickers).replaceAll(" ", "")).toUpperCase();
  const expected = (req.body.expected).replaceAll(" ", "");
  const confidences = (req.body.confidences).replaceAll(" ", "");
  let dataIn = [];

  // run python script of black litterman algorithm
  let args = ['controllers/BlackLittermanAlgorithm.py'];
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

// Random Forrest Classifier form submission
exports.respondRFCForm = (req, res) => {
  const symbol = req.body.symbol;
  const start_date = req.body.start_date;
  const end_date = req.body.end_date;
  const first_model_obs = req.body.first_model_obs;
  const step = req.body.step;
  const n_estimators = req.body.n_estimators;
  const min_samples_split = req.body.min_samples_split;
  let dataIn = [];

  // run python script of black litterman algorithm
  let args = ['controllers/RandomForestClassifier.py'];
  args.push(symbol, start_date, end_date, first_model_obs, step, n_estimators, min_samples_split);

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
    if (dataIn) {
      // split by line then first by word
      accuracy = ((dataIn.split(/\r?\n/))[1]).split(" ")[3]
    }
    res.render("rfc-form", {"symbol": symbol, "start_date": start_date, "end_date": end_date, "accuracy": accuracy});
  })
};