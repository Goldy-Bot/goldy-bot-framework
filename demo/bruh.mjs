
export default class Bruh {
    constructor() {
        console.log("NANI!");
        console.log("okay");
    }

    async hello(platter) {
        await platter.send_message("hello", {
            "reply": true
        });
    }
}