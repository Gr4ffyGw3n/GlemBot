const lib = require('lib')({token: process.env.STDLIB_SECRET_TOKEN});

await lib.discord.channels['@0.3.2'].messages.create({
  "channel_id": `${context.params.event.channel_id}`,
  "content": "",
  "tts": false,
  "components": [
    {
      "type": 1,
      "components": [
        {
          "style": 1,
          "custom_id": `row_0_button_0`,
          "disabled": false,
          "type": 2
        },
        {
          "style": 1,
          "custom_id": `row_0_button_1`,
          "disabled": false,
          "type": 2
        },
        {
          "style": 1,
          "custom_id": `row_0_button_2`,
          "disabled": false,
          "type": 2
        }
      ]
    }
  ],
  "embeds": [
    {
      "type": "rich",
      "title": `Toast's Stage`,
      "description": "",
      "color": 0x00FFFF,
      "image": {
        "url": `https://ibb.co/QbdTK4V`,
        "height": 0,
        "width": 0
      }
    }
  ]
});