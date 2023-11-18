const express = require('express');
const app = express();
const port = process.env.PORT || 3000;
const Cloudant = require('@cloudant/cloudant');

// Initialize Cloudant connection
function dbCloudantConnect(dbName) {
    return new Promise((resolve, reject) => {
    Cloudant({ url: 'https://f64d2e29-560f-4f25-99ab-e921d3cf5eef-bluemix.cloudantnosqldb.appdomain.cloud', maxAttempt: 5, plugins: [ { iamauth: { iamApiKey: 'mri0rdU4SawrOwFFxE2KwLE7pYeLN1bgl8wWsH3I7z-s' } }, { retry: { retryDelayMultiplier: 4 } } ]}, ((err, cloudant) => {
            if (err) {
                console.error('Connect failure: ' + err.message + ' for Cloudant DB');
                reject(err);
            } else {
                let db = cloudant.use(dbName);
                console.info('Connect success! Connected to DB: ' + dbName);
                resolve(db);
            }
        }));
    });
}

let dealershipsDB, reviewsDB;

dbCloudantConnect("dealerships").then((database) => {
    dealershipsDB = database;
}).catch((err) => {
    throw err;
});


dbCloudantConnect("reviews").then((database) => {
    reviewsDB = database;
}).catch((err) => {
    throw err;
});

app.use(express.json());
app.set('json spaces', 2);

// Define a route to get all dealerships with optional state and ID filters
app.get('/api/dealership', (req, res) => {
    const { state, id } = req.query;

    // If no params, empty selector will be sent and all docs will be retrieved.
    let selector = {};

    if (id) selector.id = parseInt(id);
    if (state) selector.state = state;

    dealershipsDB.find({ selector: selector }, (err, result) => {
        if (err) {
            return res.status(500).send({ error: "Something went wrong on the server" });
        }
        if (result.docs.length == 0){
            if (state){
                return res.status(404).send({ error: "The state does not exist" });
            }
            return res.status(404).send({ error: "The database is empty" });
        }
        res.json(result.docs);
    });
});

// This must be implemented with Python-Flask, its just temporary
app.get('/api/review', (req, res) => {
    const { dealerId } = req.query;

    let selector = {}

    if(dealerId)
        selector.dealership = parseInt(dealerId)

    reviewsDB.find({selector: selector}, (err, result) => {
        if(err) {
            return res.status(500).send({ error: "Something went wrong on the server" });
        }
        if (result.docs.length == 0){
            if (dealerId){
                return res.status(404).send({ error: "Dealership does not exist" });
            }
            return res.status(404).send({ error: "The database is empty" });
        }

        res.json(result.docs)
    })
})

app.listen(port, () => {
    console.log("Listening to port " + port)
})