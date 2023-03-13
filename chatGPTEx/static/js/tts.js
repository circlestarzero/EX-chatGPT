const enableChinese = true;
// https://clearn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts
const createSpeechConfig = (() => {
    let speechConfig;
    return async () => {
        if (!speechConfig) {
            try {
                const response = await fetch('/api/getAzureAPIKey');
                const data = await response.json();
                const subscriptionKey = data.subscriptionKey;
                const region = data.region;
                console.log('Subscription Key:', subscriptionKey);
                console.log('Region:', region);
                speechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, region);
                speechConfig.speechRecognitionLanguage = "en-US";
                if (enableChinese) {
                    speechConfig.speechRecognitionLanguage = "zh-CN";
                }
            } catch (error) {
                console.error('Error fetching Azure API Key:', error);
            }
        }

        return speechConfig;
    };
})();
let synthesizer;
async function TTS(text) {
    if (!synthesizer) {
        const speechConfig = await createSpeechConfig();
        synthesizer = new SpeechSDK.SpeechSynthesizer(speechConfig);
      }
    const EnglishSsml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="en-US-JennyNeural">
    <prosody rate="+40.00%">
        ${text}
    </prosody>
</voice>
</speak>`;
    const ChineseSsml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
<voice name="zh-CN-XiaoshuangNeural">
    <prosody rate="+55.00%">
        ${text}
    </prosody>
</voice>
</speak>`;
    var ssml;
    if (enableChinese) {
        ssml = ChineseSsml;
    } else {
        ssml = EnglishSsml;
    }
    return new Promise((resolve, reject) => {
        synthesizer.speakSsmlAsync(
            ssml,
            (result) => {
                if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
                    console.log(`synthesis finished for [${text}].\n`);
                    resolve();
                } else if (result.reason === SpeechSDK.ResultReason.Canceled) {
                    console.log(`synthesis failed. Error detail: ${result.errorDetails}\n`);
                    reject(result.errorDetails);
                }
                window.console.log(result);
            },
            (err) => {
                window.console.log(err);
                reject(err);
            }
        );
    });
}
var enableRecord = false
var lastRecordmsg = ''
let speechRecognizer
async function fromMic() {
    if(!speechRecognizer){
        const speechConfig = await createSpeechConfig();
        const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
        speechRecognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);
    }
    console.log(enableRecord)
    if (enableRecord) {
        speechRecognizer.stopContinuousRecognitionAsync();
        enableRecord = false;
        return;
    }
    lastRecordmsg = msgerInput.value;
    speechRecognizer.recognizing = (s, e) => {
        console.log(`RECOGNIZING: Text=${e.result.text}`);
        msgerInput.value = lastRecordmsg + e.result.text;
        textAreaHeightAdjut();
    };
    speechRecognizer.recognized = (s, e) => {
        enableRecord = true;
        if (e.result.reason == SpeechSDK.ResultReason.RecognizedSpeech) {
            textAreaHeightAdjut();
            msgerInput.value = lastRecordmsg + e.result.text;
            lastRecordmsg = msgerInput.value
            console.log(`RECOGNIZED: Text=${e.result.text}`);
        }
        else if (e.result.reason == SpeechSDK.ResultReason.NoMatch) {
            console.log("NOMATCH: Speech could not be recognized.");
        }
    };
    speechRecognizer.canceled = (s, e) => {
        enableRecord = false;
        console.log(`CANCELED: Reason=${e.reason}`);
        if (e.reason == SpeechSDK.CancellationReason.Error) {
            console.log(`"CANCELED: ErrorCode=${e.errorCode}`);
            console.log(`"CANCELED: ErrorDetails=${e.errorDetails}`);
            console.log("CANCELED: Did you set the speech resource key and region values?");
        }
        speechRecognizer.stopContinuousRecognitionAsync();
    };
    speechRecognizer.sessionStopped = (s, e) => {
        enableRecord = false;
        console.log("\n    Session stopped event.");
        speechRecognizer.stopContinuousRecognitionAsync();
    };
    speechRecognizer.startContinuousRecognitionAsync();
    enableRecord = true;
}


