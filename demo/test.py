import sys; sys.path.insert(0, '..')

import js2py
from js2py.es6 import js6_to_js5
import GoldyBot

GoldyBot.Goldy()

context = js2py.EvalJs({'GoldyBot': GoldyBot})  

js_code = """
export default class YourExtension {
   constructor() {
      super();
   }

   async hello(platter) {
      await platter.send_message("hello", {
         "reply": true
      });
   }
}

function load() {
   new YourExtension();
}
"""

js2py.eval_js6('let a = () => 11; a()')

#context.execute(js6_to_js5(js_code))