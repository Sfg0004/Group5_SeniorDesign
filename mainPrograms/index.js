const process = require('process')
var arguments = process.argv

var index = 2;
var fileSync = arguments[2]
while (index + 1 < arguments.length) {
    var fileSync = fileSync.concat(" ", arguments[index + 1]);
    index = index + 1;
}

const Moralis = require("moralis").default;
const fs = require("fs");
require("dotenv").config();

const fileUploads = [
    {
        path: "uploaded_file",
        content: fs.readFileSync(fileSync, {encoding: "base64"})
    }
  ]

async function uploadToIpfs(){
    await Moralis.start({
        apiKey: process.env.MORALIS_KEY
    })

    const res = await Moralis.EvmApi.ipfs.uploadFolder({
        abi: fileUploads
    })

    console.log(res.result)
}

uploadToIpfs();