import * as path$1 from 'node:path';
import path__default, { dirname, join, resolve as resolve$3 } from 'node:path';
import * as fs$2 from 'node:fs';
import fs__default, { promises, readFileSync, unlink, existsSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import os from 'node:os';
import { networkInterfaces } from 'os';
import crypto, { randomUUID } from 'crypto';
import crypto$1 from 'node:crypto';
import fs$3 from 'fs';
import log4js from 'log4js';
import process$2, { pid, ppid, exit } from 'node:process';
import tty from 'node:tty';
import fsPromise$1, { open, stat as stat$1 } from 'node:fs/promises';
import ffmpeg from 'fluent-ffmpeg';
import fsPromise from 'fs/promises';
import 'util';
import { isSilk, isWav, getWavFileInfo, encode, getDuration } from 'silk-wasm';
import require$$1$1, { spawn } from 'node:child_process';
import { ReadableStream } from 'node:stream/web';
import { PassThrough, pipeline } from 'node:stream';
import path$2 from 'path';
import require$$1 from 'events';
import https$1 from 'node:https';
import http$1 from 'node:http';
import express, { Router } from 'express';
import { WebSocketServer, WebSocket as WebSocket$1 } from 'ws';
import http$2 from 'http';
import urlParse from 'url';
import require$$0 from 'node:events';
import qrcode from 'qrcode-terminal';
import * as net from 'node:net';

let osName;
let machineId;
try {
  osName = os.hostname();
} catch (e) {
  osName = "NapCat";
}
const invalidMacAddresses = /* @__PURE__ */ new Set(["00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff", "ac:de:48:00:11:22"]);
function validateMacAddress(candidate) {
  const tempCandidate = candidate.replace(/\-/g, ":").toLowerCase();
  return !invalidMacAddresses.has(tempCandidate);
}
async function getMachineId() {
  if (!machineId) {
    machineId = (async () => {
      const id = await getMacMachineId();
      return id || randomUUID();
    })();
  }
  return machineId;
}
function getMac() {
  const ifaces = networkInterfaces();
  for (const name in ifaces) {
    const networkInterface = ifaces[name];
    if (networkInterface) {
      for (const {
        mac
      } of networkInterface) {
        if (validateMacAddress(mac)) {
          return mac;
        }
      }
    }
  }
  throw new Error("Unable to retrieve mac address (unexpected format)");
}
async function getMacMachineId() {
  try {
    const crypto = await import('crypto');
    const macAddress = getMac();
    return crypto.createHash("sha256").update(macAddress, "utf8").digest("hex");
  } catch (err) {
    return void 0;
  }
}
const homeDir = os.homedir();
const systemPlatform = os.platform();
os.arch();
const systemVersion = os.release();
const hostname = osName;
path__default.join(homeDir, "Downloads");
const systemName = os.type();

const ANSI_BACKGROUND_OFFSET = 10;
const wrapAnsi16 = (offset = 0) => code => `\u001B[${code + offset}m`;
const wrapAnsi256 = (offset = 0) => code => `\u001B[${38 + offset};5;${code}m`;
const wrapAnsi16m = (offset = 0) => (red, green, blue) => `\u001B[${38 + offset};2;${red};${green};${blue}m`;
const styles$1 = {
  modifier: {
    reset: [0, 0],
    // 21 isn't widely supported and 22 does the same thing
    bold: [1, 22],
    dim: [2, 22],
    italic: [3, 23],
    underline: [4, 24],
    overline: [53, 55],
    inverse: [7, 27],
    hidden: [8, 28],
    strikethrough: [9, 29]
  },
  color: {
    black: [30, 39],
    red: [31, 39],
    green: [32, 39],
    yellow: [33, 39],
    blue: [34, 39],
    magenta: [35, 39],
    cyan: [36, 39],
    white: [37, 39],
    // Bright color
    blackBright: [90, 39],
    gray: [90, 39],
    // Alias of `blackBright`
    grey: [90, 39],
    // Alias of `blackBright`
    redBright: [91, 39],
    greenBright: [92, 39],
    yellowBright: [93, 39],
    blueBright: [94, 39],
    magentaBright: [95, 39],
    cyanBright: [96, 39],
    whiteBright: [97, 39]
  },
  bgColor: {
    bgBlack: [40, 49],
    bgRed: [41, 49],
    bgGreen: [42, 49],
    bgYellow: [43, 49],
    bgBlue: [44, 49],
    bgMagenta: [45, 49],
    bgCyan: [46, 49],
    bgWhite: [47, 49],
    // Bright color
    bgBlackBright: [100, 49],
    bgGray: [100, 49],
    // Alias of `bgBlackBright`
    bgGrey: [100, 49],
    // Alias of `bgBlackBright`
    bgRedBright: [101, 49],
    bgGreenBright: [102, 49],
    bgYellowBright: [103, 49],
    bgBlueBright: [104, 49],
    bgMagentaBright: [105, 49],
    bgCyanBright: [106, 49],
    bgWhiteBright: [107, 49]
  }
};
Object.keys(styles$1.modifier);
const foregroundColorNames = Object.keys(styles$1.color);
const backgroundColorNames = Object.keys(styles$1.bgColor);
[...foregroundColorNames, ...backgroundColorNames];
function assembleStyles() {
  const codes = new Map();
  for (const [groupName, group] of Object.entries(styles$1)) {
    for (const [styleName, style] of Object.entries(group)) {
      styles$1[styleName] = {
        open: `\u001B[${style[0]}m`,
        close: `\u001B[${style[1]}m`
      };
      group[styleName] = styles$1[styleName];
      codes.set(style[0], style[1]);
    }
    Object.defineProperty(styles$1, groupName, {
      value: group,
      enumerable: false
    });
  }
  Object.defineProperty(styles$1, 'codes', {
    value: codes,
    enumerable: false
  });
  styles$1.color.close = '\u001B[39m';
  styles$1.bgColor.close = '\u001B[49m';
  styles$1.color.ansi = wrapAnsi16();
  styles$1.color.ansi256 = wrapAnsi256();
  styles$1.color.ansi16m = wrapAnsi16m();
  styles$1.bgColor.ansi = wrapAnsi16(ANSI_BACKGROUND_OFFSET);
  styles$1.bgColor.ansi256 = wrapAnsi256(ANSI_BACKGROUND_OFFSET);
  styles$1.bgColor.ansi16m = wrapAnsi16m(ANSI_BACKGROUND_OFFSET);

  // From https://github.com/Qix-/color-convert/blob/3f0e0d4e92e235796ccb17f6e85c72094a651f49/conversions.js
  Object.defineProperties(styles$1, {
    rgbToAnsi256: {
      value(red, green, blue) {
        // We use the extended greyscale palette here, with the exception of
        // black and white. normal palette only has 4 greyscale shades.
        if (red === green && green === blue) {
          if (red < 8) {
            return 16;
          }
          if (red > 248) {
            return 231;
          }
          return Math.round((red - 8) / 247 * 24) + 232;
        }
        return 16 + 36 * Math.round(red / 255 * 5) + 6 * Math.round(green / 255 * 5) + Math.round(blue / 255 * 5);
      },
      enumerable: false
    },
    hexToRgb: {
      value(hex) {
        const matches = /[a-f\d]{6}|[a-f\d]{3}/i.exec(hex.toString(16));
        if (!matches) {
          return [0, 0, 0];
        }
        let [colorString] = matches;
        if (colorString.length === 3) {
          colorString = [...colorString].map(character => character + character).join('');
        }
        const integer = Number.parseInt(colorString, 16);
        return [/* eslint-disable no-bitwise */
        integer >> 16 & 0xFF, integer >> 8 & 0xFF, integer & 0xFF
        /* eslint-enable no-bitwise */];
      },
      enumerable: false
    },
    hexToAnsi256: {
      value: hex => styles$1.rgbToAnsi256(...styles$1.hexToRgb(hex)),
      enumerable: false
    },
    ansi256ToAnsi: {
      value(code) {
        if (code < 8) {
          return 30 + code;
        }
        if (code < 16) {
          return 90 + (code - 8);
        }
        let red;
        let green;
        let blue;
        if (code >= 232) {
          red = ((code - 232) * 10 + 8) / 255;
          green = red;
          blue = red;
        } else {
          code -= 16;
          const remainder = code % 36;
          red = Math.floor(code / 36) / 5;
          green = Math.floor(remainder / 6) / 5;
          blue = remainder % 6 / 5;
        }
        const value = Math.max(red, green, blue) * 2;
        if (value === 0) {
          return 30;
        }

        // eslint-disable-next-line no-bitwise
        let result = 30 + (Math.round(blue) << 2 | Math.round(green) << 1 | Math.round(red));
        if (value === 2) {
          result += 60;
        }
        return result;
      },
      enumerable: false
    },
    rgbToAnsi: {
      value: (red, green, blue) => styles$1.ansi256ToAnsi(styles$1.rgbToAnsi256(red, green, blue)),
      enumerable: false
    },
    hexToAnsi: {
      value: hex => styles$1.ansi256ToAnsi(styles$1.hexToAnsi256(hex)),
      enumerable: false
    }
  });
  return styles$1;
}
const ansiStyles = assembleStyles();

// From: https://github.com/sindresorhus/has-flag/blob/main/index.js
/// function hasFlag(flag, argv = globalThis.Deno?.args ?? process.argv) {
function hasFlag(flag, argv = globalThis.Deno ? globalThis.Deno.args : process$2.argv) {
  const prefix = flag.startsWith('-') ? '' : flag.length === 1 ? '-' : '--';
  const position = argv.indexOf(prefix + flag);
  const terminatorPosition = argv.indexOf('--');
  return position !== -1 && (terminatorPosition === -1 || position < terminatorPosition);
}
const {
  env
} = process$2;
let flagForceColor;
if (hasFlag('no-color') || hasFlag('no-colors') || hasFlag('color=false') || hasFlag('color=never')) {
  flagForceColor = 0;
} else if (hasFlag('color') || hasFlag('colors') || hasFlag('color=true') || hasFlag('color=always')) {
  flagForceColor = 1;
}
function envForceColor() {
  if ('FORCE_COLOR' in env) {
    if (env.FORCE_COLOR === 'true') {
      return 1;
    }
    if (env.FORCE_COLOR === 'false') {
      return 0;
    }
    return env.FORCE_COLOR.length === 0 ? 1 : Math.min(Number.parseInt(env.FORCE_COLOR, 10), 3);
  }
}
function translateLevel(level) {
  if (level === 0) {
    return false;
  }
  return {
    level,
    hasBasic: true,
    has256: level >= 2,
    has16m: level >= 3
  };
}
function _supportsColor(haveStream, {
  streamIsTTY,
  sniffFlags = true
} = {}) {
  const noFlagForceColor = envForceColor();
  if (noFlagForceColor !== undefined) {
    flagForceColor = noFlagForceColor;
  }
  const forceColor = sniffFlags ? flagForceColor : noFlagForceColor;
  if (forceColor === 0) {
    return 0;
  }
  if (sniffFlags) {
    if (hasFlag('color=16m') || hasFlag('color=full') || hasFlag('color=truecolor')) {
      return 3;
    }
    if (hasFlag('color=256')) {
      return 2;
    }
  }

  // Check for Azure DevOps pipelines.
  // Has to be above the `!streamIsTTY` check.
  if ('TF_BUILD' in env && 'AGENT_NAME' in env) {
    return 1;
  }
  if (haveStream && !streamIsTTY && forceColor === undefined) {
    return 0;
  }
  const min = forceColor || 0;
  if (env.TERM === 'dumb') {
    return min;
  }
  if (process$2.platform === 'win32') {
    // Windows 10 build 10586 is the first Windows release that supports 256 colors.
    // Windows 10 build 14931 is the first release that supports 16m/TrueColor.
    const osRelease = os.release().split('.');
    if (Number(osRelease[0]) >= 10 && Number(osRelease[2]) >= 10_586) {
      return Number(osRelease[2]) >= 14_931 ? 3 : 2;
    }
    return 1;
  }
  if ('CI' in env) {
    if ('GITHUB_ACTIONS' in env || 'GITEA_ACTIONS' in env) {
      return 3;
    }
    if (['TRAVIS', 'CIRCLECI', 'APPVEYOR', 'GITLAB_CI', 'BUILDKITE', 'DRONE'].some(sign => sign in env) || env.CI_NAME === 'codeship') {
      return 1;
    }
    return min;
  }
  if ('TEAMCITY_VERSION' in env) {
    return /^(9\.(0*[1-9]\d*)\.|\d{2,}\.)/.test(env.TEAMCITY_VERSION) ? 1 : 0;
  }
  if (env.COLORTERM === 'truecolor') {
    return 3;
  }
  if (env.TERM === 'xterm-kitty') {
    return 3;
  }
  if ('TERM_PROGRAM' in env) {
    const version = Number.parseInt((env.TERM_PROGRAM_VERSION || '').split('.')[0], 10);
    switch (env.TERM_PROGRAM) {
      case 'iTerm.app':
        {
          return version >= 3 ? 3 : 2;
        }
      case 'Apple_Terminal':
        {
          return 2;
        }
      // No default
    }
  }
  if (/-256(color)?$/i.test(env.TERM)) {
    return 2;
  }
  if (/^screen|^xterm|^vt100|^vt220|^rxvt|color|ansi|cygwin|linux/i.test(env.TERM)) {
    return 1;
  }
  if ('COLORTERM' in env) {
    return 1;
  }
  return min;
}
function createSupportsColor(stream, options = {}) {
  const level = _supportsColor(stream, {
    streamIsTTY: stream && stream.isTTY,
    ...options
  });
  return translateLevel(level);
}
const supportsColor = {
  stdout: createSupportsColor({
    isTTY: tty.isatty(1)
  }),
  stderr: createSupportsColor({
    isTTY: tty.isatty(2)
  })
};

// TODO: When targeting Node.js 16, use `String.prototype.replaceAll`.
function stringReplaceAll(string, substring, replacer) {
  let index = string.indexOf(substring);
  if (index === -1) {
    return string;
  }
  const substringLength = substring.length;
  let endIndex = 0;
  let returnValue = '';
  do {
    returnValue += string.slice(endIndex, index) + substring + replacer;
    endIndex = index + substringLength;
    index = string.indexOf(substring, endIndex);
  } while (index !== -1);
  returnValue += string.slice(endIndex);
  return returnValue;
}
function stringEncaseCRLFWithFirstIndex(string, prefix, postfix, index) {
  let endIndex = 0;
  let returnValue = '';
  do {
    const gotCR = string[index - 1] === '\r';
    returnValue += string.slice(endIndex, gotCR ? index - 1 : index) + prefix + (gotCR ? '\r\n' : '\n') + postfix;
    endIndex = index + 1;
    index = string.indexOf('\n', endIndex);
  } while (index !== -1);
  returnValue += string.slice(endIndex);
  return returnValue;
}

const {
  stdout: stdoutColor,
  stderr: stderrColor
} = supportsColor;
const GENERATOR = Symbol('GENERATOR');
const STYLER = Symbol('STYLER');
const IS_EMPTY = Symbol('IS_EMPTY');

// `supportsColor.level` → `ansiStyles.color[name]` mapping
const levelMapping = ['ansi', 'ansi', 'ansi256', 'ansi16m'];
const styles = Object.create(null);
const applyOptions = (object, options = {}) => {
  if (options.level && !(Number.isInteger(options.level) && options.level >= 0 && options.level <= 3)) {
    throw new Error('The `level` option should be an integer from 0 to 3');
  }

  // Detect level if not set manually
  const colorLevel = stdoutColor ? stdoutColor.level : 0;
  object.level = options.level === undefined ? colorLevel : options.level;
};
const chalkFactory = options => {
  const chalk = (...strings) => strings.join(' ');
  applyOptions(chalk, options);
  Object.setPrototypeOf(chalk, createChalk.prototype);
  return chalk;
};
function createChalk(options) {
  return chalkFactory(options);
}
Object.setPrototypeOf(createChalk.prototype, Function.prototype);
for (const [styleName, style] of Object.entries(ansiStyles)) {
  styles[styleName] = {
    get() {
      const builder = createBuilder(this, createStyler(style.open, style.close, this[STYLER]), this[IS_EMPTY]);
      Object.defineProperty(this, styleName, {
        value: builder
      });
      return builder;
    }
  };
}
styles.visible = {
  get() {
    const builder = createBuilder(this, this[STYLER], true);
    Object.defineProperty(this, 'visible', {
      value: builder
    });
    return builder;
  }
};
const getModelAnsi = (model, level, type, ...arguments_) => {
  if (model === 'rgb') {
    if (level === 'ansi16m') {
      return ansiStyles[type].ansi16m(...arguments_);
    }
    if (level === 'ansi256') {
      return ansiStyles[type].ansi256(ansiStyles.rgbToAnsi256(...arguments_));
    }
    return ansiStyles[type].ansi(ansiStyles.rgbToAnsi(...arguments_));
  }
  if (model === 'hex') {
    return getModelAnsi('rgb', level, type, ...ansiStyles.hexToRgb(...arguments_));
  }
  return ansiStyles[type][model](...arguments_);
};
const usedModels = ['rgb', 'hex', 'ansi256'];
for (const model of usedModels) {
  styles[model] = {
    get() {
      const {
        level
      } = this;
      return function (...arguments_) {
        const styler = createStyler(getModelAnsi(model, levelMapping[level], 'color', ...arguments_), ansiStyles.color.close, this[STYLER]);
        return createBuilder(this, styler, this[IS_EMPTY]);
      };
    }
  };
  const bgModel = 'bg' + model[0].toUpperCase() + model.slice(1);
  styles[bgModel] = {
    get() {
      const {
        level
      } = this;
      return function (...arguments_) {
        const styler = createStyler(getModelAnsi(model, levelMapping[level], 'bgColor', ...arguments_), ansiStyles.bgColor.close, this[STYLER]);
        return createBuilder(this, styler, this[IS_EMPTY]);
      };
    }
  };
}
const proto = Object.defineProperties(() => {}, {
  ...styles,
  level: {
    enumerable: true,
    get() {
      return this[GENERATOR].level;
    },
    set(level) {
      this[GENERATOR].level = level;
    }
  }
});
const createStyler = (open, close, parent) => {
  let openAll;
  let closeAll;
  if (parent === undefined) {
    openAll = open;
    closeAll = close;
  } else {
    openAll = parent.openAll + open;
    closeAll = close + parent.closeAll;
  }
  return {
    open,
    close,
    openAll,
    closeAll,
    parent
  };
};
const createBuilder = (self, _styler, _isEmpty) => {
  // Single argument is hot path, implicit coercion is faster than anything
  // eslint-disable-next-line no-implicit-coercion
  const builder = (...arguments_) => applyStyle(builder, arguments_.length === 1 ? '' + arguments_[0] : arguments_.join(' '));

  // We alter the prototype because we must return a function, but there is
  // no way to create a function with a different prototype
  Object.setPrototypeOf(builder, proto);
  builder[GENERATOR] = self;
  builder[STYLER] = _styler;
  builder[IS_EMPTY] = _isEmpty;
  return builder;
};
const applyStyle = (self, string) => {
  if (self.level <= 0 || !string) {
    return self[IS_EMPTY] ? '' : string;
  }
  let styler = self[STYLER];
  if (styler === undefined) {
    return string;
  }
  const {
    openAll,
    closeAll
  } = styler;
  if (string.includes('\u001B')) {
    while (styler !== undefined) {
      // Replace any instances already present with a re-opening code
      // otherwise only the part of the string until said closing code
      // will be colored, and the rest will simply be 'plain'.
      string = stringReplaceAll(string, styler.close, styler.open);
      styler = styler.parent;
    }
  }

  // We can move both next actions out of loop, because remaining actions in loop won't have
  // any/visible effect on parts we add here. Close the styling before a linebreak and reopen
  // after next line to fix a bleed issue on macOS: https://github.com/chalk/chalk/pull/92
  const lfIndex = string.indexOf('\n');
  if (lfIndex !== -1) {
    string = stringEncaseCRLFWithFirstIndex(string, closeAll, openAll, lfIndex);
  }
  return openAll + string + closeAll;
};
Object.defineProperties(createChalk.prototype, styles);
const chalk = createChalk();
createChalk({
  level: stderrColor ? stderrColor.level : 0
});

const __filename$8 = fileURLToPath(import.meta.url);
const __dirname$6 = dirname(__filename$8);
let LogLevel = /* @__PURE__ */ function(LogLevel2) {
  LogLevel2["DEBUG"] = "debug";
  LogLevel2["INFO"] = "info";
  LogLevel2["WARN"] = "warn";
  LogLevel2["ERROR"] = "error";
  LogLevel2["FATAL"] = "fatal";
  return LogLevel2;
}({});
const logDir = path__default.join(path__default.resolve(__dirname$6), "logs");
function getFormattedTimestamp() {
  const now = /* @__PURE__ */ new Date();
  const year = now.getFullYear();
  const month = (now.getMonth() + 1).toString().padStart(2, "0");
  const day = now.getDate().toString().padStart(2, "0");
  const hours = now.getHours().toString().padStart(2, "0");
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const seconds = now.getSeconds().toString().padStart(2, "0");
  const milliseconds = now.getMilliseconds().toString().padStart(3, "0");
  return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}.${milliseconds}`;
}
const filename = `${getFormattedTimestamp()}.log`;
const logPath = path__default.join(logDir, filename);
const logConfig = {
  appenders: {
    FileAppender: {
      // 输出到文件的appender
      type: "file",
      filename: logPath,
      // 指定日志文件的位置和文件名
      maxLogSize: 10485760,
      // 日志文件的最大大小（单位：字节），这里设置为10MB
      layout: {
        type: "pattern",
        pattern: "%d{yyyy-MM-dd hh:mm:ss} [%p] %X{userInfo} | %m"
      }
    },
    ConsoleAppender: {
      // 输出到控制台的appender
      type: "console",
      layout: {
        type: "pattern",
        pattern: `%d{yyyy-MM-dd hh:mm:ss} [%[%p%]] ${chalk.magenta("%X{userInfo}")} | %m`
      }
    }
  },
  categories: {
    default: {
      appenders: ["FileAppender", "ConsoleAppender"],
      level: "debug"
    },
    // 默认情况下同时输出到文件和控制台
    file: {
      appenders: ["FileAppender"],
      level: "debug"
    },
    console: {
      appenders: ["ConsoleAppender"],
      level: "debug"
    }
  }
};
log4js.configure(logConfig);
const loggerConsole = log4js.getLogger("console");
const loggerFile = log4js.getLogger("file");
const loggerDefault = log4js.getLogger("default");
function setLogLevel(fileLogLevel, consoleLogLevel) {
  logConfig.categories.file.level = fileLogLevel;
  logConfig.categories.console.level = consoleLogLevel;
  log4js.configure(logConfig);
}
function setLogSelfInfo(selfInfo) {
  const userInfo = `${selfInfo.nick}(${selfInfo.uin})`;
  loggerConsole.addContext("userInfo", userInfo);
  loggerFile.addContext("userInfo", userInfo);
  loggerDefault.addContext("userInfo", userInfo);
}
setLogSelfInfo({
  nick: "",
  uin: "",
  uid: ""
});
let fileLogEnabled = true;
let consoleLogEnabled = true;
function enableFileLog(enable) {
  fileLogEnabled = enable;
}
function enableConsoleLog(enable) {
  consoleLogEnabled = enable;
}
function formatMsg(msg) {
  let logMsg = "";
  for (const msgItem of msg) {
    if (msgItem instanceof Error) {
      logMsg += msgItem.stack + " ";
      continue;
    } else if (typeof msgItem === "object") {
      const obj = JSON.parse(JSON.stringify(msgItem, null, 2));
      logMsg += JSON.stringify(truncateString(obj)) + " ";
      continue;
    }
    logMsg += msgItem + " ";
  }
  return logMsg;
}
const colorEscape = /\x1B[@-_][0-?]*[ -/]*[@-~]/g;
function _log(level, ...args) {
  if (consoleLogEnabled) {
    loggerConsole[level](formatMsg(args));
  }
  if (fileLogEnabled) {
    loggerFile[level](formatMsg(args).replace(colorEscape, ""));
  }
}
function log(...args) {
  _log(LogLevel.INFO, ...args);
}
function logDebug(...args) {
  _log(LogLevel.DEBUG, ...args);
}
function logError(...args) {
  _log(LogLevel.ERROR, ...args);
}
function logWarn(...args) {
  _log(LogLevel.WARN, ...args);
}

const __filename$7 = fileURLToPath(import.meta.url);
dirname(__filename$7);
class UUIDConverter {
  static encode(highStr, lowStr) {
    const high = BigInt(highStr);
    const low = BigInt(lowStr);
    const highHex = high.toString(16).padStart(16, "0");
    const lowHex = low.toString(16).padStart(16, "0");
    const combinedHex = highHex + lowHex;
    const uuid = `${combinedHex.substring(0, 8)}-${combinedHex.substring(8, 12)}-${combinedHex.substring(12, 16)}-${combinedHex.substring(16, 20)}-${combinedHex.substring(20)}`;
    return uuid;
  }
  static decode(uuid) {
    const hex = uuid.replace(/-/g, "");
    const high = BigInt("0x" + hex.substring(0, 16));
    const low = BigInt("0x" + hex.substring(16));
    return {
      high: high.toString(),
      low: low.toString()
    };
  }
}
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
function PromiseTimer(promise, ms) {
  const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error("PromiseTimer: Operation timed out")), ms));
  return Promise.race([promise, timeoutPromise]);
}
async function runAllWithTimeout(tasks, timeout) {
  const wrappedTasks = tasks.map((task) => PromiseTimer(task, timeout).then((result) => ({
    status: "fulfilled",
    value: result
  }), (error) => ({
    status: "rejected",
    reason: error
  })));
  const results = await Promise.all(wrappedTasks);
  return results.filter((result) => result.status === "fulfilled").map((result) => result.value);
}
function isNull(value) {
  return value === void 0 || value === null;
}
function isNumeric(str) {
  return /^\d+$/.test(str);
}
function truncateString(obj, maxLength = 500) {
  if (obj !== null && typeof obj === "object") {
    Object.keys(obj).forEach((key) => {
      if (typeof obj[key] === "string") {
        if (obj[key].length > maxLength) {
          obj[key] = obj[key].substring(0, maxLength) + "...";
        }
      } else if (typeof obj[key] === "object") {
        truncateString(obj[key], maxLength);
      }
    });
  }
  return obj;
}
function CacheClassFuncAsync(ttl = 3600 * 1e3, customKey = "") {
  function logExecutionTime(target, methodName, descriptor) {
    const cache = /* @__PURE__ */ new Map();
    const originalMethod = descriptor.value;
    descriptor.value = async function(...args) {
      const key = `${customKey}${String(methodName)}.(${args.map((arg) => JSON.stringify(arg)).join(", ")})`;
      cache.forEach((value, key2) => {
        if (value.expiry < Date.now()) {
          cache.delete(key2);
        }
      });
      const cachedValue = cache.get(key);
      if (cachedValue && cachedValue.expiry > Date.now()) {
        return cachedValue.value;
      }
      const result = await originalMethod.apply(this, args);
      cache.set(key, {
        expiry: Date.now() + ttl,
        value: result
      });
      return result;
    };
  }
  return logExecutionTime;
}
function CacheClassFuncAsyncExtend(ttl = 3600 * 1e3, customKey = "", checker = (...data) => {
  return true;
}) {
  function logExecutionTime(target, methodName, descriptor) {
    const cache = /* @__PURE__ */ new Map();
    const originalMethod = descriptor.value;
    descriptor.value = async function(...args) {
      const key = `${customKey}${String(methodName)}.(${args.map((arg) => JSON.stringify(arg)).join(", ")})`;
      cache.forEach((value, key2) => {
        if (value.expiry < Date.now()) {
          cache.delete(key2);
        }
      });
      const cachedValue = cache.get(key);
      if (cachedValue && cachedValue.expiry > Date.now()) {
        return cachedValue.value;
      }
      const result = await originalMethod.apply(this, args);
      if (!checker(...args, result)) {
        return result;
      }
      cache.set(key, {
        expiry: Date.now() + ttl,
        value: result
      });
      return result;
    };
  }
  return logExecutionTime;
}
function isEqual(obj1, obj2) {
  if (obj1 === obj2) return true;
  if (obj1 == null || obj2 == null) return false;
  if (typeof obj1 !== "object" || typeof obj2 !== "object") return obj1 === obj2;
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  if (keys1.length !== keys2.length) return false;
  for (const key of keys1) {
    if (!isEqual(obj1[key], obj2[key])) return false;
  }
  return true;
}
function getDefaultQQVersionConfigInfo() {
  if (os.platform() === "linux") {
    return {
      baseVersion: "3.2.12-26702",
      curVersion: "3.2.12-26702",
      prevVersion: "",
      onErrorVersions: [],
      buildId: "26702"
    };
  }
  return {
    baseVersion: "9.9.15-26702",
    curVersion: "9.9.15-26702",
    prevVersion: "",
    onErrorVersions: [],
    buildId: "26702"
  };
}
function getQQVersionConfigPath(exePath = "") {
  let configVersionInfoPath;
  if (os.platform() !== "linux") {
    configVersionInfoPath = path__default.join(path__default.dirname(exePath), "resources", "app", "versions", "config.json");
  } else {
    const userPath = os.homedir();
    const appDataPath = path__default.resolve(userPath, "./.config/QQ");
    configVersionInfoPath = path__default.resolve(appDataPath, "./versions/config.json");
  }
  if (typeof configVersionInfoPath !== "string") {
    return void 0;
  }
  if (!fs$3.existsSync(configVersionInfoPath)) {
    return void 0;
  }
  return configVersionInfoPath;
}

const AppidTable = {
	"3.1.2-13107": {
	appid: 537146866,
	qua: "V1_LNX_NQ_3.1.2-13107_RDM_B"
},
	"3.2.10-25765": {
	appid: 537234773,
	qua: "V1_LNX_NQ_3.2.10_25765_GW_B"
},
	"3.2.12-26702": {
	appid: 537237950,
	qua: "V1_LNX_NQ_3.2.12_26702_GW_B"
},
	"3.2.12-26740": {
	appid: 537237950,
	qua: "V1_WIN_NQ_9.9.15_26740_GW_B"
},
	"9.9.11-24815": {
	appid: 537226656,
	qua: "V1_WIN_NQ_9.9.11_24815_GW_B"
},
	"9.9.12-25493": {
	appid: 537231759,
	qua: "V1_WIN_NQ_9.9.12_25493_GW_B"
},
	"9.9.12-25765": {
	appid: 537234702,
	qua: "V1_WIN_NQ_9.9.12_25765_GW_B"
},
	"9.9.12-26299": {
	appid: 537234826,
	qua: "V1_WIN_NQ_9.9.12_26299_GW_B"
},
	"9.9.12-26339": {
	appid: 537234826,
	qua: "V1_WIN_NQ_9.9.12_26339_GW_B"
},
	"9.9.12-26466": {
	appid: 537234826,
	qua: "V1_WIN_NQ_9.9.12_26466_GW_B"
},
	"9.9.15-26702": {
	appid: 537237765,
	qua: "V1_WIN_NQ_9.9.15_26702_GW_B"
},
	"9.9.15-26740": {
	appid: 537237765,
	qua: "V1_WIN_NQ_9.9.15_26702_GW_B"
}
};

const QQMainPath = process.execPath;
const QQPackageInfoPath = path__default.join(path__default.dirname(QQMainPath), "resources", "app", "package.json");
const QQVersionConfigPath = getQQVersionConfigPath(QQMainPath);
const isQuickUpdate = !!QQVersionConfigPath;
const QQVersionConfig = isQuickUpdate ? JSON.parse(fs__default.readFileSync(QQVersionConfigPath).toString()) : getDefaultQQVersionConfigInfo();
const QQPackageInfo = JSON.parse(fs__default.readFileSync(QQPackageInfoPath).toString());
const {
  appid: QQVersionAppid,
  qua: QQVersionQua
} = getAppidV2();
function getQQBuildStr() {
  return isQuickUpdate ? QQVersionConfig.buildId : QQPackageInfo.buildVersion;
}
function getFullQQVesion() {
  return isQuickUpdate ? QQVersionConfig.curVersion : QQPackageInfo.version;
}
function requireMinNTQQBuild(buildStr) {
  return parseInt(getQQBuildStr()) >= parseInt(buildStr);
}
function getQUAInternal() {
  return systemPlatform === "linux" ? `V1_LNX_NQ_${getFullQQVesion()}_${getQQBuildStr()}_GW_B` : `V1_WIN_NQ_${getFullQQVesion()}_${getQQBuildStr()}_GW_B`;
}
function getAppidV2() {
  const appidTbale = AppidTable;
  try {
    const data = appidTbale[getFullQQVesion()];
    if (data) {
      return data;
    }
  } catch (e) {
    log("[QQ版本兼容性检测] 获取Appid异常 请检测NapCat/QQNT是否正常");
  }
  log(`[QQ版本兼容性检测] ${getFullQQVesion()} 版本兼容性不佳，可能会导致一些功能无法正常使用`);
  return {
    appid: systemPlatform === "linux" ? "537237950" : "537237765",
    qua: getQUAInternal()
  };
}

const __filename$6 = fileURLToPath(import.meta.url);
dirname(__filename$6);
let wrapperNodePath = path__default.resolve(path__default.dirname(process.execPath), "./resources/app/wrapper.node");
if (!fs__default.existsSync(wrapperNodePath)) {
  wrapperNodePath = path__default.join(path__default.dirname(process.execPath), `resources/app/versions/${getFullQQVesion()}/wrapper.node`);
}
const nativemodule = {
  exports: {}
};
process.dlopen(nativemodule, wrapperNodePath);
const QQWrapper = nativemodule.exports;

class DependsAdapter {
  onMSFStatusChange(arg1, arg2) {
  }
  onMSFSsoError(args) {
  }
  getGroupCode(args) {
  }
}

class DispatcherAdapter {
  dispatchRequest(arg) {
  }
  dispatchCall(arg) {
  }
  dispatchCallWithJson(arg) {
  }
}

class GlobalAdapter {
  onLog(...args) {
  }
  onGetSrvCalTime(...args) {
  }
  onShowErrUITips(...args) {
  }
  fixPicImgType(...args) {
  }
  getAppSetting(...args) {
  }
  onInstallFinished(...args) {
  }
  onUpdateGeneralFlag(...args) {
  }
  onGetOfflineMsg(...args) {
  }
}

let Sex = /* @__PURE__ */ function(Sex2) {
  Sex2[Sex2["male"] = 1] = "male";
  Sex2[Sex2["female"] = 2] = "female";
  Sex2[Sex2["unknown"] = 255] = "unknown";
  return Sex2;
}({});

let GroupMemberRole = /* @__PURE__ */ function(GroupMemberRole2) {
  GroupMemberRole2[GroupMemberRole2["normal"] = 2] = "normal";
  GroupMemberRole2[GroupMemberRole2["admin"] = 3] = "admin";
  GroupMemberRole2[GroupMemberRole2["owner"] = 4] = "owner";
  return GroupMemberRole2;
}({});

let ElementType = /* @__PURE__ */ function(ElementType2) {
  ElementType2[ElementType2["UNKNOWN"] = 0] = "UNKNOWN";
  ElementType2[ElementType2["TEXT"] = 1] = "TEXT";
  ElementType2[ElementType2["PIC"] = 2] = "PIC";
  ElementType2[ElementType2["FILE"] = 3] = "FILE";
  ElementType2[ElementType2["PTT"] = 4] = "PTT";
  ElementType2[ElementType2["VIDEO"] = 5] = "VIDEO";
  ElementType2[ElementType2["FACE"] = 6] = "FACE";
  ElementType2[ElementType2["REPLY"] = 7] = "REPLY";
  ElementType2[ElementType2["WALLET"] = 9] = "WALLET";
  ElementType2[ElementType2["GreyTip"] = 8] = "GreyTip";
  ElementType2[ElementType2["ARK"] = 10] = "ARK";
  ElementType2[ElementType2["MFACE"] = 11] = "MFACE";
  ElementType2[ElementType2["LIVEGIFT"] = 12] = "LIVEGIFT";
  ElementType2[ElementType2["STRUCTLONGMSG"] = 13] = "STRUCTLONGMSG";
  ElementType2[ElementType2["MARKDOWN"] = 14] = "MARKDOWN";
  ElementType2[ElementType2["GIPHY"] = 15] = "GIPHY";
  ElementType2[ElementType2["MULTIFORWARD"] = 16] = "MULTIFORWARD";
  ElementType2[ElementType2["INLINEKEYBOARD"] = 17] = "INLINEKEYBOARD";
  ElementType2[ElementType2["INTEXTGIFT"] = 18] = "INTEXTGIFT";
  ElementType2[ElementType2["CALENDAR"] = 19] = "CALENDAR";
  ElementType2[ElementType2["YOLOGAMERESULT"] = 20] = "YOLOGAMERESULT";
  ElementType2[ElementType2["AVRECORD"] = 21] = "AVRECORD";
  ElementType2[ElementType2["FEED"] = 22] = "FEED";
  ElementType2[ElementType2["TOFURECORD"] = 23] = "TOFURECORD";
  ElementType2[ElementType2["ACEBUBBLE"] = 24] = "ACEBUBBLE";
  ElementType2[ElementType2["ACTIVITY"] = 25] = "ACTIVITY";
  ElementType2[ElementType2["TOFU"] = 26] = "TOFU";
  ElementType2[ElementType2["FACEBUBBLE"] = 27] = "FACEBUBBLE";
  ElementType2[ElementType2["SHARELOCATION"] = 28] = "SHARELOCATION";
  ElementType2[ElementType2["TASKTOPMSG"] = 29] = "TASKTOPMSG";
  ElementType2[ElementType2["RECOMMENDEDMSG"] = 43] = "RECOMMENDEDMSG";
  ElementType2[ElementType2["ACTIONBAR"] = 44] = "ACTIONBAR";
  return ElementType2;
}({});
let PicType = /* @__PURE__ */ function(PicType2) {
  PicType2[PicType2["gif"] = 2e3] = "gif";
  PicType2[PicType2["jpg"] = 1e3] = "jpg";
  return PicType2;
}({});
let AtType = /* @__PURE__ */ function(AtType2) {
  AtType2[AtType2["notAt"] = 0] = "notAt";
  AtType2[AtType2["atAll"] = 1] = "atAll";
  AtType2[AtType2["atUser"] = 2] = "atUser";
  return AtType2;
}({});
let ChatType = /* @__PURE__ */ function(ChatType3) {
  ChatType3[ChatType3["friend"] = 1] = "friend";
  ChatType3[ChatType3["group"] = 2] = "group";
  ChatType3[ChatType3["chatDevice"] = 8] = "chatDevice";
  ChatType3[ChatType3["temp"] = 100] = "temp";
  return ChatType3;
}({});
let ChatType2 = /* @__PURE__ */ function(ChatType22) {
  ChatType22[ChatType22["KCHATTYPEADELIE"] = 42] = "KCHATTYPEADELIE";
  ChatType22[ChatType22["KCHATTYPEBUDDYNOTIFY"] = 5] = "KCHATTYPEBUDDYNOTIFY";
  ChatType22[ChatType22["KCHATTYPEC2C"] = 1] = "KCHATTYPEC2C";
  ChatType22[ChatType22["KCHATTYPECIRCLE"] = 113] = "KCHATTYPECIRCLE";
  ChatType22[ChatType22["KCHATTYPEDATALINE"] = 8] = "KCHATTYPEDATALINE";
  ChatType22[ChatType22["KCHATTYPEDATALINEMQQ"] = 134] = "KCHATTYPEDATALINEMQQ";
  ChatType22[ChatType22["KCHATTYPEDISC"] = 3] = "KCHATTYPEDISC";
  ChatType22[ChatType22["KCHATTYPEFAV"] = 41] = "KCHATTYPEFAV";
  ChatType22[ChatType22["KCHATTYPEGAMEMESSAGE"] = 105] = "KCHATTYPEGAMEMESSAGE";
  ChatType22[ChatType22["KCHATTYPEGAMEMESSAGEFOLDER"] = 116] = "KCHATTYPEGAMEMESSAGEFOLDER";
  ChatType22[ChatType22["KCHATTYPEGROUP"] = 2] = "KCHATTYPEGROUP";
  ChatType22[ChatType22["KCHATTYPEGROUPBLESS"] = 133] = "KCHATTYPEGROUPBLESS";
  ChatType22[ChatType22["KCHATTYPEGROUPGUILD"] = 9] = "KCHATTYPEGROUPGUILD";
  ChatType22[ChatType22["KCHATTYPEGROUPHELPER"] = 7] = "KCHATTYPEGROUPHELPER";
  ChatType22[ChatType22["KCHATTYPEGROUPNOTIFY"] = 6] = "KCHATTYPEGROUPNOTIFY";
  ChatType22[ChatType22["KCHATTYPEGUILD"] = 4] = "KCHATTYPEGUILD";
  ChatType22[ChatType22["KCHATTYPEGUILDMETA"] = 16] = "KCHATTYPEGUILDMETA";
  ChatType22[ChatType22["KCHATTYPEMATCHFRIEND"] = 104] = "KCHATTYPEMATCHFRIEND";
  ChatType22[ChatType22["KCHATTYPEMATCHFRIENDFOLDER"] = 109] = "KCHATTYPEMATCHFRIENDFOLDER";
  ChatType22[ChatType22["KCHATTYPENEARBY"] = 106] = "KCHATTYPENEARBY";
  ChatType22[ChatType22["KCHATTYPENEARBYASSISTANT"] = 107] = "KCHATTYPENEARBYASSISTANT";
  ChatType22[ChatType22["KCHATTYPENEARBYFOLDER"] = 110] = "KCHATTYPENEARBYFOLDER";
  ChatType22[ChatType22["KCHATTYPENEARBYHELLOFOLDER"] = 112] = "KCHATTYPENEARBYHELLOFOLDER";
  ChatType22[ChatType22["KCHATTYPENEARBYINTERACT"] = 108] = "KCHATTYPENEARBYINTERACT";
  ChatType22[ChatType22["KCHATTYPEQQNOTIFY"] = 132] = "KCHATTYPEQQNOTIFY";
  ChatType22[ChatType22["KCHATTYPERELATEACCOUNT"] = 131] = "KCHATTYPERELATEACCOUNT";
  ChatType22[ChatType22["KCHATTYPESERVICEASSISTANT"] = 118] = "KCHATTYPESERVICEASSISTANT";
  ChatType22[ChatType22["KCHATTYPESERVICEASSISTANTSUB"] = 201] = "KCHATTYPESERVICEASSISTANTSUB";
  ChatType22[ChatType22["KCHATTYPESQUAREPUBLIC"] = 115] = "KCHATTYPESQUAREPUBLIC";
  ChatType22[ChatType22["KCHATTYPESUBSCRIBEFOLDER"] = 30] = "KCHATTYPESUBSCRIBEFOLDER";
  ChatType22[ChatType22["KCHATTYPETEMPADDRESSBOOK"] = 111] = "KCHATTYPETEMPADDRESSBOOK";
  ChatType22[ChatType22["KCHATTYPETEMPBUSSINESSCRM"] = 102] = "KCHATTYPETEMPBUSSINESSCRM";
  ChatType22[ChatType22["KCHATTYPETEMPC2CFROMGROUP"] = 100] = "KCHATTYPETEMPC2CFROMGROUP";
  ChatType22[ChatType22["KCHATTYPETEMPC2CFROMUNKNOWN"] = 99] = "KCHATTYPETEMPC2CFROMUNKNOWN";
  ChatType22[ChatType22["KCHATTYPETEMPFRIENDVERIFY"] = 101] = "KCHATTYPETEMPFRIENDVERIFY";
  ChatType22[ChatType22["KCHATTYPETEMPNEARBYPRO"] = 119] = "KCHATTYPETEMPNEARBYPRO";
  ChatType22[ChatType22["KCHATTYPETEMPPUBLICACCOUNT"] = 103] = "KCHATTYPETEMPPUBLICACCOUNT";
  ChatType22[ChatType22["KCHATTYPETEMPWPA"] = 117] = "KCHATTYPETEMPWPA";
  ChatType22[ChatType22["KCHATTYPEUNKNOWN"] = 0] = "KCHATTYPEUNKNOWN";
  ChatType22[ChatType22["KCHATTYPEWEIYUN"] = 40] = "KCHATTYPEWEIYUN";
  return ChatType22;
}({});
const IMAGE_HTTP_HOST = "https://gchat.qpic.cn";
const IMAGE_HTTP_HOST_NT = "https://multimedia.nt.qq.com.cn";
let GrayTipElementSubType = /* @__PURE__ */ function(GrayTipElementSubType2) {
  GrayTipElementSubType2[GrayTipElementSubType2["INVITE_NEW_MEMBER"] = 12] = "INVITE_NEW_MEMBER";
  GrayTipElementSubType2[GrayTipElementSubType2["MEMBER_NEW_TITLE"] = 17] = "MEMBER_NEW_TITLE";
  return GrayTipElementSubType2;
}({});
let FaceType = /* @__PURE__ */ function(FaceType2) {
  FaceType2[FaceType2["normal"] = 1] = "normal";
  FaceType2[FaceType2["normal2"] = 2] = "normal2";
  FaceType2[FaceType2["dice"] = 3] = "dice";
  return FaceType2;
}({});
let FaceIndex = /* @__PURE__ */ function(FaceIndex2) {
  FaceIndex2[FaceIndex2["dice"] = 358] = "dice";
  FaceIndex2[FaceIndex2["RPS"] = 359] = "RPS";
  return FaceIndex2;
}({});
let viedo_type = /* @__PURE__ */ function(viedo_type2) {
  viedo_type2[viedo_type2["VIDEO_FORMAT_AFS"] = 7] = "VIDEO_FORMAT_AFS";
  viedo_type2[viedo_type2["VIDEO_FORMAT_AVI"] = 1] = "VIDEO_FORMAT_AVI";
  viedo_type2[viedo_type2["VIDEO_FORMAT_MKV"] = 4] = "VIDEO_FORMAT_MKV";
  viedo_type2[viedo_type2["VIDEO_FORMAT_MOD"] = 9] = "VIDEO_FORMAT_MOD";
  viedo_type2[viedo_type2["VIDEO_FORMAT_MOV"] = 8] = "VIDEO_FORMAT_MOV";
  viedo_type2[viedo_type2["VIDEO_FORMAT_MP4"] = 2] = "VIDEO_FORMAT_MP4";
  viedo_type2[viedo_type2["VIDEO_FORMAT_MTS"] = 11] = "VIDEO_FORMAT_MTS";
  viedo_type2[viedo_type2["VIDEO_FORMAT_RM"] = 6] = "VIDEO_FORMAT_RM";
  viedo_type2[viedo_type2["VIDEO_FORMAT_RMVB"] = 5] = "VIDEO_FORMAT_RMVB";
  viedo_type2[viedo_type2["VIDEO_FORMAT_TS"] = 10] = "VIDEO_FORMAT_TS";
  viedo_type2[viedo_type2["VIDEO_FORMAT_WMV"] = 3] = "VIDEO_FORMAT_WMV";
  return viedo_type2;
}({});
let TipGroupElementType = /* @__PURE__ */ function(TipGroupElementType2) {
  TipGroupElementType2[TipGroupElementType2["memberIncrease"] = 1] = "memberIncrease";
  TipGroupElementType2[TipGroupElementType2["kicked"] = 3] = "kicked";
  TipGroupElementType2[TipGroupElementType2["ban"] = 8] = "ban";
  return TipGroupElementType2;
}({});

let GroupNotifyTypes = /* @__PURE__ */ function(GroupNotifyTypes2) {
  GroupNotifyTypes2[GroupNotifyTypes2["INVITE_ME"] = 1] = "INVITE_ME";
  GroupNotifyTypes2[GroupNotifyTypes2["INVITED_JOIN"] = 4] = "INVITED_JOIN";
  GroupNotifyTypes2[GroupNotifyTypes2["JOIN_REQUEST"] = 7] = "JOIN_REQUEST";
  GroupNotifyTypes2[GroupNotifyTypes2["ADMIN_SET"] = 8] = "ADMIN_SET";
  GroupNotifyTypes2[GroupNotifyTypes2["KICK_MEMBER"] = 9] = "KICK_MEMBER";
  GroupNotifyTypes2[GroupNotifyTypes2["MEMBER_EXIT"] = 11] = "MEMBER_EXIT";
  GroupNotifyTypes2[GroupNotifyTypes2["ADMIN_UNSET"] = 12] = "ADMIN_UNSET";
  GroupNotifyTypes2[GroupNotifyTypes2["ADMIN_UNSET_OTHER"] = 13] = "ADMIN_UNSET_OTHER";
  return GroupNotifyTypes2;
}({});
let GroupRequestOperateTypes = /* @__PURE__ */ function(GroupRequestOperateTypes2) {
  GroupRequestOperateTypes2[GroupRequestOperateTypes2["approve"] = 1] = "approve";
  GroupRequestOperateTypes2[GroupRequestOperateTypes2["reject"] = 2] = "reject";
  return GroupRequestOperateTypes2;
}({});
let BuddyReqType = /* @__PURE__ */ function(BuddyReqType2) {
  BuddyReqType2[BuddyReqType2["KMEINITIATOR"] = 0] = "KMEINITIATOR";
  BuddyReqType2[BuddyReqType2["KPEERINITIATOR"] = 1] = "KPEERINITIATOR";
  BuddyReqType2[BuddyReqType2["KMEAGREED"] = 2] = "KMEAGREED";
  BuddyReqType2[BuddyReqType2["KMEAGREEDANDADDED"] = 3] = "KMEAGREEDANDADDED";
  BuddyReqType2[BuddyReqType2["KPEERAGREED"] = 4] = "KPEERAGREED";
  BuddyReqType2[BuddyReqType2["KPEERAGREEDANDADDED"] = 5] = "KPEERAGREEDANDADDED";
  BuddyReqType2[BuddyReqType2["KPEERREFUSED"] = 6] = "KPEERREFUSED";
  BuddyReqType2[BuddyReqType2["KMEREFUSED"] = 7] = "KMEREFUSED";
  BuddyReqType2[BuddyReqType2["KMEIGNORED"] = 8] = "KMEIGNORED";
  BuddyReqType2[BuddyReqType2["KMEAGREEANYONE"] = 9] = "KMEAGREEANYONE";
  BuddyReqType2[BuddyReqType2["KMESETQUESTION"] = 10] = "KMESETQUESTION";
  BuddyReqType2[BuddyReqType2["KMEAGREEANDADDFAILED"] = 11] = "KMEAGREEANDADDFAILED";
  BuddyReqType2[BuddyReqType2["KMSGINFO"] = 12] = "KMSGINFO";
  BuddyReqType2[BuddyReqType2["KMEINITIATORWAITPEERCONFIRM"] = 13] = "KMEINITIATORWAITPEERCONFIRM";
  return BuddyReqType2;
}({});
let MemberExtSourceType = /* @__PURE__ */ function(MemberExtSourceType2) {
  MemberExtSourceType2[MemberExtSourceType2["DEFAULTTYPE"] = 0] = "DEFAULTTYPE";
  MemberExtSourceType2[MemberExtSourceType2["TITLETYPE"] = 1] = "TITLETYPE";
  MemberExtSourceType2[MemberExtSourceType2["NEWGROUPTYPE"] = 2] = "NEWGROUPTYPE";
  return MemberExtSourceType2;
}({});

const defaultMessages = 'End-Of-Stream';
/**
 * Thrown on read operation of the end of file or stream has been reached
 */
class EndOfStreamError extends Error {
  constructor() {
    super(defaultMessages);
  }
}

class Deferred {
  constructor() {
    this.resolve = () => null;
    this.reject = () => null;
    this.promise = new Promise((resolve, reject) => {
      this.reject = reject;
      this.resolve = resolve;
    });
  }
}

class AbstractStreamReader {
  constructor() {
    /**
     * Maximum request length on read-stream operation
     */
    this.maxStreamReadSize = 1 * 1024 * 1024;
    this.endOfStream = false;
    /**
     * Store peeked data
     * @type {Array}
     */
    this.peekQueue = [];
  }
  /**
   * Read ahead (peek) from stream. Subsequent read or peeks will return the same data
   * @param uint8Array - Uint8Array (or Buffer) to store data read from stream in
   * @param offset - Offset target
   * @param length - Number of bytes to read
   * @returns Number of bytes peeked
   */
  async peek(uint8Array, offset, length) {
    const bytesRead = await this.read(uint8Array, offset, length);
    this.peekQueue.push(uint8Array.subarray(offset, offset + bytesRead)); // Put read data back to peek buffer
    return bytesRead;
  }
  async read(buffer, offset, length) {
    if (length === 0) {
      return 0;
    }
    let bytesRead = this.readFromPeekBuffer(buffer, offset, length);
    bytesRead += await this.readRemainderFromStream(buffer, offset + bytesRead, length - bytesRead);
    if (bytesRead === 0) {
      throw new EndOfStreamError();
    }
    return bytesRead;
  }
  /**
   * Read chunk from stream
   * @param buffer - Target Uint8Array (or Buffer) to store data read from stream in
   * @param offset - Offset target
   * @param length - Number of bytes to read
   * @returns Number of bytes read
   */
  readFromPeekBuffer(buffer, offset, length) {
    let remaining = length;
    let bytesRead = 0;
    // consume peeked data first
    while (this.peekQueue.length > 0 && remaining > 0) {
      const peekData = this.peekQueue.pop(); // Front of queue
      if (!peekData) throw new Error('peekData should be defined');
      const lenCopy = Math.min(peekData.length, remaining);
      buffer.set(peekData.subarray(0, lenCopy), offset + bytesRead);
      bytesRead += lenCopy;
      remaining -= lenCopy;
      if (lenCopy < peekData.length) {
        // remainder back to queue
        this.peekQueue.push(peekData.subarray(lenCopy));
      }
    }
    return bytesRead;
  }
  async readRemainderFromStream(buffer, offset, initialRemaining) {
    let remaining = initialRemaining;
    let bytesRead = 0;
    // Continue reading from stream if required
    while (remaining > 0 && !this.endOfStream) {
      const reqLen = Math.min(remaining, this.maxStreamReadSize);
      const chunkLen = await this.readFromStream(buffer, offset + bytesRead, reqLen);
      if (chunkLen === 0) break;
      bytesRead += chunkLen;
      remaining -= chunkLen;
    }
    return bytesRead;
  }
}

/**
 * Node.js Readable Stream Reader
 * Ref: https://nodejs.org/api/stream.html#readable-streams
 */
class StreamReader extends AbstractStreamReader {
  constructor(s) {
    super();
    this.s = s;
    /**
     * Deferred used for postponed read request (as not data is yet available to read)
     */
    this.deferred = null;
    if (!s.read || !s.once) {
      throw new Error('Expected an instance of stream.Readable');
    }
    this.s.once('end', () => this.reject(new EndOfStreamError()));
    this.s.once('error', err => this.reject(err));
    this.s.once('close', () => this.reject(new Error('Stream closed')));
  }
  /**
   * Read chunk from stream
   * @param buffer Target Uint8Array (or Buffer) to store data read from stream in
   * @param offset Offset target
   * @param length Number of bytes to read
   * @returns Number of bytes read
   */
  async readFromStream(buffer, offset, length) {
    if (this.endOfStream) {
      return 0;
    }
    const readBuffer = this.s.read(length);
    if (readBuffer) {
      buffer.set(readBuffer, offset);
      return readBuffer.length;
    }
    const request = {
      buffer,
      offset,
      length,
      deferred: new Deferred()
    };
    this.deferred = request.deferred;
    this.s.once('readable', () => {
      this.readDeferred(request);
    });
    return request.deferred.promise;
  }
  /**
   * Process deferred read request
   * @param request Deferred read request
   */
  readDeferred(request) {
    const readBuffer = this.s.read(request.length);
    if (readBuffer) {
      request.buffer.set(readBuffer, request.offset);
      request.deferred.resolve(readBuffer.length);
      this.deferred = null;
    } else {
      this.s.once('readable', () => {
        this.readDeferred(request);
      });
    }
  }
  reject(err) {
    this.endOfStream = true;
    if (this.deferred) {
      this.deferred.reject(err);
      this.deferred = null;
    }
  }
}

/**
 * Read from a WebStream
 * Reference: https://nodejs.org/api/webstreams.html#class-readablestreambyobreader
 */
class WebStreamReader extends AbstractStreamReader {
  constructor(stream) {
    super();
    this.reader = stream.getReader({
      mode: 'byob'
    });
  }
  async readFromStream(buffer, offset, length) {
    if (this.endOfStream) {
      throw new EndOfStreamError();
    }
    const result = await this.reader.read(new Uint8Array(length));
    if (result.done) {
      this.endOfStream = result.done;
    }
    if (result.value) {
      buffer.set(result.value, offset);
      return result.value.byteLength;
    }
    return 0;
  }
}

/**
 * Core tokenizer
 */
class AbstractTokenizer {
  /**
   * Constructor
   * @param options Tokenizer options
   * @protected
   */
  constructor(options) {
    var _a;
    /**
     * Tokenizer-stream position
     */
    this.position = 0;
    this.numBuffer = new Uint8Array(8);
    this.fileInfo = (_a = options === null || options === void 0 ? void 0 : options.fileInfo) !== null && _a !== void 0 ? _a : {};
    this.onClose = options === null || options === void 0 ? void 0 : options.onClose;
  }
  /**
   * Read a token from the tokenizer-stream
   * @param token - The token to read
   * @param position - If provided, the desired position in the tokenizer-stream
   * @returns Promise with token data
   */
  async readToken(token, position = this.position) {
    const uint8Array = new Uint8Array(token.len);
    const len = await this.readBuffer(uint8Array, {
      position
    });
    if (len < token.len) throw new EndOfStreamError();
    return token.get(uint8Array, 0);
  }
  /**
   * Peek a token from the tokenizer-stream.
   * @param token - Token to peek from the tokenizer-stream.
   * @param position - Offset where to begin reading within the file. If position is null, data will be read from the current file position.
   * @returns Promise with token data
   */
  async peekToken(token, position = this.position) {
    const uint8Array = new Uint8Array(token.len);
    const len = await this.peekBuffer(uint8Array, {
      position
    });
    if (len < token.len) throw new EndOfStreamError();
    return token.get(uint8Array, 0);
  }
  /**
   * Read a numeric token from the stream
   * @param token - Numeric token
   * @returns Promise with number
   */
  async readNumber(token) {
    const len = await this.readBuffer(this.numBuffer, {
      length: token.len
    });
    if (len < token.len) throw new EndOfStreamError();
    return token.get(this.numBuffer, 0);
  }
  /**
   * Read a numeric token from the stream
   * @param token - Numeric token
   * @returns Promise with number
   */
  async peekNumber(token) {
    const len = await this.peekBuffer(this.numBuffer, {
      length: token.len
    });
    if (len < token.len) throw new EndOfStreamError();
    return token.get(this.numBuffer, 0);
  }
  /**
   * Ignore number of bytes, advances the pointer in under tokenizer-stream.
   * @param length - Number of bytes to ignore
   * @return resolves the number of bytes ignored, equals length if this available, otherwise the number of bytes available
   */
  async ignore(length) {
    if (this.fileInfo.size !== undefined) {
      const bytesLeft = this.fileInfo.size - this.position;
      if (length > bytesLeft) {
        this.position += bytesLeft;
        return bytesLeft;
      }
    }
    this.position += length;
    return length;
  }
  async close() {
    var _a;
    await ((_a = this.onClose) === null || _a === void 0 ? void 0 : _a.call(this));
  }
  normalizeOptions(uint8Array, options) {
    if (options && options.position !== undefined && options.position < this.position) {
      throw new Error('`options.position` must be equal or greater than `tokenizer.position`');
    }
    if (options) {
      return {
        mayBeLess: options.mayBeLess === true,
        offset: options.offset ? options.offset : 0,
        length: options.length ? options.length : uint8Array.length - (options.offset ? options.offset : 0),
        position: options.position ? options.position : this.position
      };
    }
    return {
      mayBeLess: false,
      offset: 0,
      length: uint8Array.length,
      position: this.position
    };
  }
}

const maxBufferSize = 256000;
class ReadStreamTokenizer extends AbstractTokenizer {
  /**
   * Constructor
   * @param streamReader stream-reader to read from
   * @param options Tokenizer options
   */
  constructor(streamReader, options) {
    super(options);
    this.streamReader = streamReader;
  }
  /**
   * Read buffer from tokenizer
   * @param uint8Array - Target Uint8Array to fill with data read from the tokenizer-stream
   * @param options - Read behaviour options
   * @returns Promise with number of bytes read
   */
  async readBuffer(uint8Array, options) {
    const normOptions = this.normalizeOptions(uint8Array, options);
    const skipBytes = normOptions.position - this.position;
    if (skipBytes > 0) {
      await this.ignore(skipBytes);
      return this.readBuffer(uint8Array, options);
    }
    if (skipBytes < 0) {
      throw new Error('`options.position` must be equal or greater than `tokenizer.position`');
    }
    if (normOptions.length === 0) {
      return 0;
    }
    const bytesRead = await this.streamReader.read(uint8Array, normOptions.offset, normOptions.length);
    this.position += bytesRead;
    if ((!options || !options.mayBeLess) && bytesRead < normOptions.length) {
      throw new EndOfStreamError();
    }
    return bytesRead;
  }
  /**
   * Peek (read ahead) buffer from tokenizer
   * @param uint8Array - Uint8Array (or Buffer) to write data to
   * @param options - Read behaviour options
   * @returns Promise with number of bytes peeked
   */
  async peekBuffer(uint8Array, options) {
    const normOptions = this.normalizeOptions(uint8Array, options);
    let bytesRead = 0;
    if (normOptions.position) {
      const skipBytes = normOptions.position - this.position;
      if (skipBytes > 0) {
        const skipBuffer = new Uint8Array(normOptions.length + skipBytes);
        bytesRead = await this.peekBuffer(skipBuffer, {
          mayBeLess: normOptions.mayBeLess
        });
        uint8Array.set(skipBuffer.subarray(skipBytes), normOptions.offset);
        return bytesRead - skipBytes;
      }
      if (skipBytes < 0) {
        throw new Error('Cannot peek from a negative offset in a stream');
      }
    }
    if (normOptions.length > 0) {
      try {
        bytesRead = await this.streamReader.peek(uint8Array, normOptions.offset, normOptions.length);
      } catch (err) {
        if ((options === null || options === void 0 ? void 0 : options.mayBeLess) && err instanceof EndOfStreamError) {
          return 0;
        }
        throw err;
      }
      if (!normOptions.mayBeLess && bytesRead < normOptions.length) {
        throw new EndOfStreamError();
      }
    }
    return bytesRead;
  }
  async ignore(length) {
    // debug(`ignore ${this.position}...${this.position + length - 1}`);
    const bufSize = Math.min(maxBufferSize, length);
    const buf = new Uint8Array(bufSize);
    let totBytesRead = 0;
    while (totBytesRead < length) {
      const remaining = length - totBytesRead;
      const bytesRead = await this.readBuffer(buf, {
        length: Math.min(bufSize, remaining)
      });
      if (bytesRead < 0) {
        return bytesRead;
      }
      totBytesRead += bytesRead;
    }
    return totBytesRead;
  }
}

class BufferTokenizer extends AbstractTokenizer {
  /**
   * Construct BufferTokenizer
   * @param uint8Array - Uint8Array to tokenize
   * @param options Tokenizer options
   */
  constructor(uint8Array, options) {
    super(options);
    this.uint8Array = uint8Array;
    this.fileInfo.size = this.fileInfo.size ? this.fileInfo.size : uint8Array.length;
  }
  /**
   * Read buffer from tokenizer
   * @param uint8Array - Uint8Array to tokenize
   * @param options - Read behaviour options
   * @returns {Promise<number>}
   */
  async readBuffer(uint8Array, options) {
    if (options === null || options === void 0 ? void 0 : options.position) {
      if (options.position < this.position) {
        throw new Error('`options.position` must be equal or greater than `tokenizer.position`');
      }
      this.position = options.position;
    }
    const bytesRead = await this.peekBuffer(uint8Array, options);
    this.position += bytesRead;
    return bytesRead;
  }
  /**
   * Peek (read ahead) buffer from tokenizer
   * @param uint8Array
   * @param options - Read behaviour options
   * @returns {Promise<number>}
   */
  async peekBuffer(uint8Array, options) {
    const normOptions = this.normalizeOptions(uint8Array, options);
    const bytes2read = Math.min(this.uint8Array.length - normOptions.position, normOptions.length);
    if (!normOptions.mayBeLess && bytes2read < normOptions.length) {
      throw new EndOfStreamError();
    }
    uint8Array.set(this.uint8Array.subarray(normOptions.position, normOptions.position + bytes2read), normOptions.offset);
    return bytes2read;
  }
  close() {
    return super.close();
  }
}

/**
 * Construct ReadStreamTokenizer from given Stream.
 * Will set fileSize, if provided given Stream has set the .path property/
 * @param stream - Read from Node.js Stream.Readable
 * @param options - Tokenizer options
 * @returns ReadStreamTokenizer
 */
function fromStream$1(stream, options) {
  return new ReadStreamTokenizer(new StreamReader(stream), options);
}
/**
 * Construct ReadStreamTokenizer from given ReadableStream (WebStream API).
 * Will set fileSize, if provided given Stream has set the .path property/
 * @param webStream - Read from Node.js Stream.Readable (must be a byte stream)
 * @param options - Tokenizer options
 * @returns ReadStreamTokenizer
 */
function fromWebStream(webStream, options) {
  return new ReadStreamTokenizer(new WebStreamReader(webStream), options);
}
/**
 * Construct ReadStreamTokenizer from given Buffer.
 * @param uint8Array - Uint8Array to tokenize
 * @param options - Tokenizer options
 * @returns BufferTokenizer
 */
function fromBuffer(uint8Array, options) {
  return new BufferTokenizer(uint8Array, options);
}

class FileTokenizer extends AbstractTokenizer {
  constructor(fileHandle, options) {
    super(options);
    this.fileHandle = fileHandle;
  }
  /**
   * Read buffer from file
   * @param uint8Array - Uint8Array to write result to
   * @param options - Read behaviour options
   * @returns Promise number of bytes read
   */
  async readBuffer(uint8Array, options) {
    const normOptions = this.normalizeOptions(uint8Array, options);
    this.position = normOptions.position;
    if (normOptions.length === 0) return 0;
    const res = await this.fileHandle.read(uint8Array, normOptions.offset, normOptions.length, normOptions.position);
    this.position += res.bytesRead;
    if (res.bytesRead < normOptions.length && (!options || !options.mayBeLess)) {
      throw new EndOfStreamError();
    }
    return res.bytesRead;
  }
  /**
   * Peek buffer from file
   * @param uint8Array - Uint8Array (or Buffer) to write data to
   * @param options - Read behaviour options
   * @returns Promise number of bytes read
   */
  async peekBuffer(uint8Array, options) {
    const normOptions = this.normalizeOptions(uint8Array, options);
    const res = await this.fileHandle.read(uint8Array, normOptions.offset, normOptions.length, normOptions.position);
    if (!normOptions.mayBeLess && res.bytesRead < normOptions.length) {
      throw new EndOfStreamError();
    }
    return res.bytesRead;
  }
  async close() {
    await this.fileHandle.close();
    return super.close();
  }
}
async function fromFile(sourceFilePath) {
  const fileHandle = await open(sourceFilePath, 'r');
  const stat = await fileHandle.stat();
  return new FileTokenizer(fileHandle, {
    fileInfo: {
      path: sourceFilePath,
      size: stat.size
    }
  });
}

/**
 * Construct ReadStreamTokenizer from given Stream.
 * Will set fileSize, if provided given Stream has set the .path property.
 * @param stream - Node.js Stream.Readable
 * @param options - Pass additional file information to the tokenizer
 * @returns Tokenizer
 */
async function fromStream(stream, options) {
  var _a;
  const augmentedOptions = {};
  augmentedOptions.fileInfo = (_a = augmentedOptions.fileInfo) !== null && _a !== void 0 ? _a : {};
  if (stream.path) {
    const stat = await stat$1(stream.path);
    augmentedOptions.fileInfo.path = stream.path;
    augmentedOptions.fileInfo.size = stat.size;
  }
  return fromStream$1(stream, augmentedOptions);
}

function getDefaultExportFromCjs (x) {
	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
}

// Primitive types
function dv(array) {
  return new DataView(array.buffer, array.byteOffset);
}
/**
 * 8-bit unsigned integer
 */
const UINT8 = {
  len: 1,
  get(array, offset) {
    return dv(array).getUint8(offset);
  },
  put(array, offset, value) {
    dv(array).setUint8(offset, value);
    return offset + 1;
  }
};
/**
 * 16-bit unsigned integer, Little Endian byte order
 */
const UINT16_LE = {
  len: 2,
  get(array, offset) {
    return dv(array).getUint16(offset, true);
  },
  put(array, offset, value) {
    dv(array).setUint16(offset, value, true);
    return offset + 2;
  }
};
/**
 * 16-bit unsigned integer, Big Endian byte order
 */
const UINT16_BE = {
  len: 2,
  get(array, offset) {
    return dv(array).getUint16(offset);
  },
  put(array, offset, value) {
    dv(array).setUint16(offset, value);
    return offset + 2;
  }
};
/**
 * 32-bit unsigned integer, Little Endian byte order
 */
const UINT32_LE = {
  len: 4,
  get(array, offset) {
    return dv(array).getUint32(offset, true);
  },
  put(array, offset, value) {
    dv(array).setUint32(offset, value, true);
    return offset + 4;
  }
};
/**
 * 32-bit unsigned integer, Big Endian byte order
 */
const UINT32_BE = {
  len: 4,
  get(array, offset) {
    return dv(array).getUint32(offset);
  },
  put(array, offset, value) {
    dv(array).setUint32(offset, value);
    return offset + 4;
  }
};
/**
 * 32-bit signed integer, Big Endian byte order
 */
const INT32_BE = {
  len: 4,
  get(array, offset) {
    return dv(array).getInt32(offset);
  },
  put(array, offset, value) {
    dv(array).setInt32(offset, value);
    return offset + 4;
  }
};
/**
 * 64-bit unsigned integer, Little Endian byte order
 */
const UINT64_LE = {
  len: 8,
  get(array, offset) {
    return dv(array).getBigUint64(offset, true);
  },
  put(array, offset, value) {
    dv(array).setBigUint64(offset, value, true);
    return offset + 8;
  }
};
/**
 * Consume a fixed number of bytes from the stream and return a string with a specified encoding.
 */
class StringType {
  constructor(len, encoding) {
    this.len = len;
    this.encoding = encoding;
    this.textDecoder = new TextDecoder(encoding);
  }
  get(uint8Array, offset) {
    return this.textDecoder.decode(uint8Array.subarray(offset, offset + this.len));
  }
}

({
  utf8: new globalThis.TextDecoder('utf8')
});
new globalThis.TextEncoder();
Array.from({
  length: 256
}, (_, index) => index.toString(16).padStart(2, '0'));

/**
@param {DataView} view
@returns {number}
*/
function getUintBE(view) {
  const {
    byteLength
  } = view;
  if (byteLength === 6) {
    return view.getUint16(0) * 2 ** 32 + view.getUint32(2);
  }
  if (byteLength === 5) {
    return view.getUint8(0) * 2 ** 32 + view.getUint32(1);
  }
  if (byteLength === 4) {
    return view.getUint32(0);
  }
  if (byteLength === 3) {
    return view.getUint8(0) * 2 ** 16 + view.getUint16(1);
  }
  if (byteLength === 2) {
    return view.getUint16(0);
  }
  if (byteLength === 1) {
    return view.getUint8(0);
  }
}

/**
@param {Uint8Array} array
@param {Uint8Array} value
@returns {number}
*/
function indexOf(array, value) {
  const arrayLength = array.length;
  const valueLength = value.length;
  if (valueLength === 0) {
    return -1;
  }
  if (valueLength > arrayLength) {
    return -1;
  }
  const validOffsetLength = arrayLength - valueLength;
  for (let index = 0; index <= validOffsetLength; index++) {
    let isMatch = true;
    for (let index2 = 0; index2 < valueLength; index2++) {
      if (array[index + index2] !== value[index2]) {
        isMatch = false;
        break;
      }
    }
    if (isMatch) {
      return index;
    }
  }
  return -1;
}

/**
@param {Uint8Array} array
@param {Uint8Array} value
@returns {boolean}
*/
function includes(array, value) {
  return indexOf(array, value) !== -1;
}

function stringToBytes(string) {
  return [...string].map(character => character.charCodeAt(0)); // eslint-disable-line unicorn/prefer-code-point
}

/**
Checks whether the TAR checksum is valid.

@param {Uint8Array} arrayBuffer - The TAR header `[offset ... offset + 512]`.
@param {number} offset - TAR header offset.
@returns {boolean} `true` if the TAR checksum is valid, otherwise `false`.
*/
function tarHeaderChecksumMatches(arrayBuffer, offset = 0) {
  const readSum = Number.parseInt(new StringType(6).get(arrayBuffer, 148).replace(/\0.*$/, '').trim(), 8); // Read sum in header
  if (Number.isNaN(readSum)) {
    return false;
  }
  let sum = 8 * 0x20; // Initialize signed bit sum

  for (let index = offset; index < offset + 148; index++) {
    sum += arrayBuffer[index];
  }
  for (let index = offset + 156; index < offset + 512; index++) {
    sum += arrayBuffer[index];
  }
  return readSum === sum;
}

/**
ID3 UINT32 sync-safe tokenizer token.
28 bits (representing up to 256MB) integer, the msb is 0 to avoid "false syncsignals".
*/
const uint32SyncSafeToken = {
  get: (buffer, offset) => buffer[offset + 3] & 0x7F | buffer[offset + 2] << 7 | buffer[offset + 1] << 14 | buffer[offset] << 21,
  len: 4
};

const extensions = ['jpg', 'png', 'apng', 'gif', 'webp', 'flif', 'xcf', 'cr2', 'cr3', 'orf', 'arw', 'dng', 'nef', 'rw2', 'raf', 'tif', 'bmp', 'icns', 'jxr', 'psd', 'indd', 'zip', 'tar', 'rar', 'gz', 'bz2', '7z', 'dmg', 'mp4', 'mid', 'mkv', 'webm', 'mov', 'avi', 'mpg', 'mp2', 'mp3', 'm4a', 'oga', 'ogg', 'ogv', 'opus', 'flac', 'wav', 'spx', 'amr', 'pdf', 'epub', 'elf', 'macho', 'exe', 'swf', 'rtf', 'wasm', 'woff', 'woff2', 'eot', 'ttf', 'otf', 'ico', 'flv', 'ps', 'xz', 'sqlite', 'nes', 'crx', 'xpi', 'cab', 'deb', 'ar', 'rpm', 'Z', 'lz', 'cfb', 'mxf', 'mts', 'blend', 'bpg', 'docx', 'pptx', 'xlsx', '3gp', '3g2', 'j2c', 'jp2', 'jpm', 'jpx', 'mj2', 'aif', 'qcp', 'odt', 'ods', 'odp', 'xml', 'mobi', 'heic', 'cur', 'ktx', 'ape', 'wv', 'dcm', 'ics', 'glb', 'pcap', 'dsf', 'lnk', 'alias', 'voc', 'ac3', 'm4v', 'm4p', 'm4b', 'f4v', 'f4p', 'f4b', 'f4a', 'mie', 'asf', 'ogm', 'ogx', 'mpc', 'arrow', 'shp', 'aac', 'mp1', 'it', 's3m', 'xm', 'ai', 'skp', 'avif', 'eps', 'lzh', 'pgp', 'asar', 'stl', 'chm', '3mf', 'zst', 'jxl', 'vcf', 'jls', 'pst', 'dwg', 'parquet', 'class', 'arj', 'cpio', 'ace', 'avro', 'icc', 'fbx', 'vsdx'];
const mimeTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/flif', 'image/x-xcf', 'image/x-canon-cr2', 'image/x-canon-cr3', 'image/tiff', 'image/bmp', 'image/vnd.ms-photo', 'image/vnd.adobe.photoshop', 'application/x-indesign', 'application/epub+zip', 'application/x-xpinstall', 'application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.spreadsheet', 'application/vnd.oasis.opendocument.presentation', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/zip', 'application/x-tar', 'application/x-rar-compressed', 'application/gzip', 'application/x-bzip2', 'application/x-7z-compressed', 'application/x-apple-diskimage', 'application/x-apache-arrow', 'video/mp4', 'audio/midi', 'video/x-matroska', 'video/webm', 'video/quicktime', 'video/vnd.avi', 'audio/wav', 'audio/qcelp', 'audio/x-ms-asf', 'video/x-ms-asf', 'application/vnd.ms-asf', 'video/mpeg', 'video/3gpp', 'audio/mpeg', 'audio/mp4',
// RFC 4337
'audio/opus', 'video/ogg', 'audio/ogg', 'application/ogg', 'audio/x-flac', 'audio/ape', 'audio/wavpack', 'audio/amr', 'application/pdf', 'application/x-elf', 'application/x-mach-binary', 'application/x-msdownload', 'application/x-shockwave-flash', 'application/rtf', 'application/wasm', 'font/woff', 'font/woff2', 'application/vnd.ms-fontobject', 'font/ttf', 'font/otf', 'image/x-icon', 'video/x-flv', 'application/postscript', 'application/eps', 'application/x-xz', 'application/x-sqlite3', 'application/x-nintendo-nes-rom', 'application/x-google-chrome-extension', 'application/vnd.ms-cab-compressed', 'application/x-deb', 'application/x-unix-archive', 'application/x-rpm', 'application/x-compress', 'application/x-lzip', 'application/x-cfb', 'application/x-mie', 'application/mxf', 'video/mp2t', 'application/x-blender', 'image/bpg', 'image/j2c', 'image/jp2', 'image/jpx', 'image/jpm', 'image/mj2', 'audio/aiff', 'application/xml', 'application/x-mobipocket-ebook', 'image/heif', 'image/heif-sequence', 'image/heic', 'image/heic-sequence', 'image/icns', 'image/ktx', 'application/dicom', 'audio/x-musepack', 'text/calendar', 'text/vcard', 'model/gltf-binary', 'application/vnd.tcpdump.pcap', 'audio/x-dsf',
// Non-standard
'application/x.ms.shortcut',
// Invented by us
'application/x.apple.alias',
// Invented by us
'audio/x-voc', 'audio/vnd.dolby.dd-raw', 'audio/x-m4a', 'image/apng', 'image/x-olympus-orf', 'image/x-sony-arw', 'image/x-adobe-dng', 'image/x-nikon-nef', 'image/x-panasonic-rw2', 'image/x-fujifilm-raf', 'video/x-m4v', 'video/3gpp2', 'application/x-esri-shape', 'audio/aac', 'audio/x-it', 'audio/x-s3m', 'audio/x-xm', 'video/MP1S', 'video/MP2P', 'application/vnd.sketchup.skp', 'image/avif', 'application/x-lzh-compressed', 'application/pgp-encrypted', 'application/x-asar', 'model/stl', 'application/vnd.ms-htmlhelp', 'model/3mf', 'image/jxl', 'application/zstd', 'image/jls', 'application/vnd.ms-outlook', 'image/vnd.dwg', 'application/x-parquet', 'application/java-vm', 'application/x-arj', 'application/x-cpio', 'application/x-ace-compressed', 'application/avro', 'application/vnd.iccprofile', 'application/x.autodesk.fbx',
// Invented by us
'application/vnd.visio'];

/**
Primary entry point, Node.js specific entry point is index.js
*/

const reasonableDetectionSizeInBytes = 4100; // A fair amount of file-types are detectable within this range.
function _check(buffer, headers, options) {
  options = {
    offset: 0,
    ...options
  };
  for (const [index, header] of headers.entries()) {
    // If a bitmask is set
    if (options.mask) {
      // If header doesn't equal `buf` with bits masked off
      if (header !== (options.mask[index] & buffer[index + options.offset])) {
        return false;
      }
    } else if (header !== buffer[index + options.offset]) {
      return false;
    }
  }
  return true;
}
class FileTypeParser {
  constructor(options) {
    this.detectors = options?.customDetectors;
    this.fromTokenizer = this.fromTokenizer.bind(this);
    this.fromBuffer = this.fromBuffer.bind(this);
    this.parse = this.parse.bind(this);
  }
  async fromTokenizer(tokenizer) {
    const initialPosition = tokenizer.position;
    for (const detector of this.detectors || []) {
      const fileType = await detector(tokenizer);
      if (fileType) {
        return fileType;
      }
      if (initialPosition !== tokenizer.position) {
        return undefined; // Cannot proceed scanning of the tokenizer is at an arbitrary position
      }
    }
    return this.parse(tokenizer);
  }
  async fromBuffer(input) {
    if (!(input instanceof Uint8Array || input instanceof ArrayBuffer)) {
      throw new TypeError(`Expected the \`input\` argument to be of type \`Uint8Array\` or \`ArrayBuffer\`, got \`${typeof input}\``);
    }
    const buffer = input instanceof Uint8Array ? input : new Uint8Array(input);
    if (!(buffer?.length > 1)) {
      return;
    }
    return this.fromTokenizer(fromBuffer(buffer));
  }
  async fromBlob(blob) {
    return this.fromStream(blob.stream());
  }
  async fromStream(stream) {
    const tokenizer = await fromWebStream(stream);
    try {
      return await this.fromTokenizer(tokenizer);
    } finally {
      await tokenizer.close();
    }
  }
  async toDetectionStream(stream, options) {
    const {
      sampleSize = reasonableDetectionSizeInBytes
    } = options;
    let detectedFileType;
    let firstChunk;
    const reader = stream.getReader({
      mode: 'byob'
    });
    try {
      // Read the first chunk from the stream
      const {
        value: chunk,
        done
      } = await reader.read(new Uint8Array(sampleSize));
      firstChunk = chunk;
      if (!done && chunk) {
        try {
          // Attempt to detect the file type from the chunk
          detectedFileType = await this.fromBuffer(chunk.slice(0, sampleSize));
        } catch (error) {
          if (!(error instanceof EndOfStreamError)) {
            throw error; // Re-throw non-EndOfStreamError
          }
          detectedFileType = undefined;
        }
      }
      firstChunk = chunk;
    } finally {
      reader.releaseLock(); // Ensure the reader is released
    }

    // Create a new ReadableStream to manage locking issues
    const transformStream = new TransformStream({
      async start(controller) {
        controller.enqueue(firstChunk); // Enqueue the initial chunk
      },
      transform(chunk, controller) {
        // Pass through the chunks without modification
        controller.enqueue(chunk);
      }
    });
    const newStream = stream.pipeThrough(transformStream);
    newStream.fileType = detectedFileType;
    return newStream;
  }
  check(header, options) {
    return _check(this.buffer, header, options);
  }
  checkString(header, options) {
    return this.check(stringToBytes(header), options);
  }
  async parse(tokenizer) {
    this.buffer = new Uint8Array(reasonableDetectionSizeInBytes);

    // Keep reading until EOF if the file size is unknown.
    if (tokenizer.fileInfo.size === undefined) {
      tokenizer.fileInfo.size = Number.MAX_SAFE_INTEGER;
    }
    this.tokenizer = tokenizer;
    await tokenizer.peekBuffer(this.buffer, {
      length: 12,
      mayBeLess: true
    });

    // -- 2-byte signatures --

    if (this.check([0x42, 0x4D])) {
      return {
        ext: 'bmp',
        mime: 'image/bmp'
      };
    }
    if (this.check([0x0B, 0x77])) {
      return {
        ext: 'ac3',
        mime: 'audio/vnd.dolby.dd-raw'
      };
    }
    if (this.check([0x78, 0x01])) {
      return {
        ext: 'dmg',
        mime: 'application/x-apple-diskimage'
      };
    }
    if (this.check([0x4D, 0x5A])) {
      return {
        ext: 'exe',
        mime: 'application/x-msdownload'
      };
    }
    if (this.check([0x25, 0x21])) {
      await tokenizer.peekBuffer(this.buffer, {
        length: 24,
        mayBeLess: true
      });
      if (this.checkString('PS-Adobe-', {
        offset: 2
      }) && this.checkString(' EPSF-', {
        offset: 14
      })) {
        return {
          ext: 'eps',
          mime: 'application/eps'
        };
      }
      return {
        ext: 'ps',
        mime: 'application/postscript'
      };
    }
    if (this.check([0x1F, 0xA0]) || this.check([0x1F, 0x9D])) {
      return {
        ext: 'Z',
        mime: 'application/x-compress'
      };
    }
    if (this.check([0xC7, 0x71])) {
      return {
        ext: 'cpio',
        mime: 'application/x-cpio'
      };
    }
    if (this.check([0x60, 0xEA])) {
      return {
        ext: 'arj',
        mime: 'application/x-arj'
      };
    }

    // -- 3-byte signatures --

    if (this.check([0xEF, 0xBB, 0xBF])) {
      // UTF-8-BOM
      // Strip off UTF-8-BOM
      this.tokenizer.ignore(3);
      return this.parse(tokenizer);
    }
    if (this.check([0x47, 0x49, 0x46])) {
      return {
        ext: 'gif',
        mime: 'image/gif'
      };
    }
    if (this.check([0x49, 0x49, 0xBC])) {
      return {
        ext: 'jxr',
        mime: 'image/vnd.ms-photo'
      };
    }
    if (this.check([0x1F, 0x8B, 0x8])) {
      return {
        ext: 'gz',
        mime: 'application/gzip'
      };
    }
    if (this.check([0x42, 0x5A, 0x68])) {
      return {
        ext: 'bz2',
        mime: 'application/x-bzip2'
      };
    }
    if (this.checkString('ID3')) {
      await tokenizer.ignore(6); // Skip ID3 header until the header size
      const id3HeaderLength = await tokenizer.readToken(uint32SyncSafeToken);
      if (tokenizer.position + id3HeaderLength > tokenizer.fileInfo.size) {
        // Guess file type based on ID3 header for backward compatibility
        return {
          ext: 'mp3',
          mime: 'audio/mpeg'
        };
      }
      await tokenizer.ignore(id3HeaderLength);
      return this.fromTokenizer(tokenizer); // Skip ID3 header, recursion
    }

    // Musepack, SV7
    if (this.checkString('MP+')) {
      return {
        ext: 'mpc',
        mime: 'audio/x-musepack'
      };
    }
    if ((this.buffer[0] === 0x43 || this.buffer[0] === 0x46) && this.check([0x57, 0x53], {
      offset: 1
    })) {
      return {
        ext: 'swf',
        mime: 'application/x-shockwave-flash'
      };
    }

    // -- 4-byte signatures --

    // Requires a sample size of 4 bytes
    if (this.check([0xFF, 0xD8, 0xFF])) {
      if (this.check([0xF7], {
        offset: 3
      })) {
        // JPG7/SOF55, indicating a ISO/IEC 14495 / JPEG-LS file
        return {
          ext: 'jls',
          mime: 'image/jls'
        };
      }
      return {
        ext: 'jpg',
        mime: 'image/jpeg'
      };
    }
    if (this.check([0x4F, 0x62, 0x6A, 0x01])) {
      return {
        ext: 'avro',
        mime: 'application/avro'
      };
    }
    if (this.checkString('FLIF')) {
      return {
        ext: 'flif',
        mime: 'image/flif'
      };
    }
    if (this.checkString('8BPS')) {
      return {
        ext: 'psd',
        mime: 'image/vnd.adobe.photoshop'
      };
    }
    if (this.checkString('WEBP', {
      offset: 8
    })) {
      return {
        ext: 'webp',
        mime: 'image/webp'
      };
    }

    // Musepack, SV8
    if (this.checkString('MPCK')) {
      return {
        ext: 'mpc',
        mime: 'audio/x-musepack'
      };
    }
    if (this.checkString('FORM')) {
      return {
        ext: 'aif',
        mime: 'audio/aiff'
      };
    }
    if (this.checkString('icns', {
      offset: 0
    })) {
      return {
        ext: 'icns',
        mime: 'image/icns'
      };
    }

    // Zip-based file formats
    // Need to be before the `zip` check
    if (this.check([0x50, 0x4B, 0x3, 0x4])) {
      // Local file header signature
      try {
        while (tokenizer.position + 30 < tokenizer.fileInfo.size) {
          await tokenizer.readBuffer(this.buffer, {
            length: 30
          });
          const view = new DataView(this.buffer.buffer);

          // https://en.wikipedia.org/wiki/Zip_(file_format)#File_headers
          const zipHeader = {
            compressedSize: view.getUint32(18, true),
            uncompressedSize: view.getUint32(22, true),
            filenameLength: view.getUint16(26, true),
            extraFieldLength: view.getUint16(28, true)
          };
          zipHeader.filename = await tokenizer.readToken(new StringType(zipHeader.filenameLength, 'utf-8'));
          await tokenizer.ignore(zipHeader.extraFieldLength);

          // Assumes signed `.xpi` from addons.mozilla.org
          if (zipHeader.filename === 'META-INF/mozilla.rsa') {
            return {
              ext: 'xpi',
              mime: 'application/x-xpinstall'
            };
          }
          if (zipHeader.filename.endsWith('.rels') || zipHeader.filename.endsWith('.xml')) {
            const type = zipHeader.filename.split('/')[0];
            switch (type) {
              case '_rels':
                break;
              case 'word':
                return {
                  ext: 'docx',
                  mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                };
              case 'ppt':
                return {
                  ext: 'pptx',
                  mime: 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                };
              case 'xl':
                return {
                  ext: 'xlsx',
                  mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                };
              case 'visio':
                return {
                  ext: 'vsdx',
                  mime: 'application/vnd.visio'
                };
              default:
                break;
            }
          }
          if (zipHeader.filename.startsWith('xl/')) {
            return {
              ext: 'xlsx',
              mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            };
          }
          if (zipHeader.filename.startsWith('3D/') && zipHeader.filename.endsWith('.model')) {
            return {
              ext: '3mf',
              mime: 'model/3mf'
            };
          }

          // The docx, xlsx and pptx file types extend the Office Open XML file format:
          // https://en.wikipedia.org/wiki/Office_Open_XML_file_formats
          // We look for:
          // - one entry named '[Content_Types].xml' or '_rels/.rels',
          // - one entry indicating specific type of file.
          // MS Office, OpenOffice and LibreOffice may put the parts in different order, so the check should not rely on it.
          if (zipHeader.filename === 'mimetype' && zipHeader.compressedSize === zipHeader.uncompressedSize) {
            let mimeType = await tokenizer.readToken(new StringType(zipHeader.compressedSize, 'utf-8'));
            mimeType = mimeType.trim();
            switch (mimeType) {
              case 'application/epub+zip':
                return {
                  ext: 'epub',
                  mime: 'application/epub+zip'
                };
              case 'application/vnd.oasis.opendocument.text':
                return {
                  ext: 'odt',
                  mime: 'application/vnd.oasis.opendocument.text'
                };
              case 'application/vnd.oasis.opendocument.spreadsheet':
                return {
                  ext: 'ods',
                  mime: 'application/vnd.oasis.opendocument.spreadsheet'
                };
              case 'application/vnd.oasis.opendocument.presentation':
                return {
                  ext: 'odp',
                  mime: 'application/vnd.oasis.opendocument.presentation'
                };
              default:
            }
          }

          // Try to find next header manually when current one is corrupted
          if (zipHeader.compressedSize === 0) {
            let nextHeaderIndex = -1;
            while (nextHeaderIndex < 0 && tokenizer.position < tokenizer.fileInfo.size) {
              await tokenizer.peekBuffer(this.buffer, {
                mayBeLess: true
              });
              nextHeaderIndex = indexOf(this.buffer, new Uint8Array([0x50, 0x4B, 0x03, 0x04]));

              // Move position to the next header if found, skip the whole buffer otherwise
              await tokenizer.ignore(nextHeaderIndex >= 0 ? nextHeaderIndex : this.buffer.length);
            }
          } else {
            await tokenizer.ignore(zipHeader.compressedSize);
          }
        }
      } catch (error) {
        if (!(error instanceof EndOfStreamError)) {
          throw error;
        }
      }
      return {
        ext: 'zip',
        mime: 'application/zip'
      };
    }
    if (this.checkString('OggS')) {
      // This is an OGG container
      await tokenizer.ignore(28);
      const type = new Uint8Array(8);
      await tokenizer.readBuffer(type);

      // Needs to be before `ogg` check
      if (_check(type, [0x4F, 0x70, 0x75, 0x73, 0x48, 0x65, 0x61, 0x64])) {
        return {
          ext: 'opus',
          mime: 'audio/opus'
        };
      }

      // If ' theora' in header.
      if (_check(type, [0x80, 0x74, 0x68, 0x65, 0x6F, 0x72, 0x61])) {
        return {
          ext: 'ogv',
          mime: 'video/ogg'
        };
      }

      // If '\x01video' in header.
      if (_check(type, [0x01, 0x76, 0x69, 0x64, 0x65, 0x6F, 0x00])) {
        return {
          ext: 'ogm',
          mime: 'video/ogg'
        };
      }

      // If ' FLAC' in header  https://xiph.org/flac/faq.html
      if (_check(type, [0x7F, 0x46, 0x4C, 0x41, 0x43])) {
        return {
          ext: 'oga',
          mime: 'audio/ogg'
        };
      }

      // 'Speex  ' in header https://en.wikipedia.org/wiki/Speex
      if (_check(type, [0x53, 0x70, 0x65, 0x65, 0x78, 0x20, 0x20])) {
        return {
          ext: 'spx',
          mime: 'audio/ogg'
        };
      }

      // If '\x01vorbis' in header
      if (_check(type, [0x01, 0x76, 0x6F, 0x72, 0x62, 0x69, 0x73])) {
        return {
          ext: 'ogg',
          mime: 'audio/ogg'
        };
      }

      // Default OGG container https://www.iana.org/assignments/media-types/application/ogg
      return {
        ext: 'ogx',
        mime: 'application/ogg'
      };
    }
    if (this.check([0x50, 0x4B]) && (this.buffer[2] === 0x3 || this.buffer[2] === 0x5 || this.buffer[2] === 0x7) && (this.buffer[3] === 0x4 || this.buffer[3] === 0x6 || this.buffer[3] === 0x8)) {
      return {
        ext: 'zip',
        mime: 'application/zip'
      };
    }

    //

    // File Type Box (https://en.wikipedia.org/wiki/ISO_base_media_file_format)
    // It's not required to be first, but it's recommended to be. Almost all ISO base media files start with `ftyp` box.
    // `ftyp` box must contain a brand major identifier, which must consist of ISO 8859-1 printable characters.
    // Here we check for 8859-1 printable characters (for simplicity, it's a mask which also catches one non-printable character).
    if (this.checkString('ftyp', {
      offset: 4
    }) && (this.buffer[8] & 0x60) !== 0x00 // Brand major, first character ASCII?
    ) {
      // They all can have MIME `video/mp4` except `application/mp4` special-case which is hard to detect.
      // For some cases, we're specific, everything else falls to `video/mp4` with `mp4` extension.
      const brandMajor = new StringType(4, 'latin1').get(this.buffer, 8).replace('\0', ' ').trim();
      switch (brandMajor) {
        case 'avif':
        case 'avis':
          return {
            ext: 'avif',
            mime: 'image/avif'
          };
        case 'mif1':
          return {
            ext: 'heic',
            mime: 'image/heif'
          };
        case 'msf1':
          return {
            ext: 'heic',
            mime: 'image/heif-sequence'
          };
        case 'heic':
        case 'heix':
          return {
            ext: 'heic',
            mime: 'image/heic'
          };
        case 'hevc':
        case 'hevx':
          return {
            ext: 'heic',
            mime: 'image/heic-sequence'
          };
        case 'qt':
          return {
            ext: 'mov',
            mime: 'video/quicktime'
          };
        case 'M4V':
        case 'M4VH':
        case 'M4VP':
          return {
            ext: 'm4v',
            mime: 'video/x-m4v'
          };
        case 'M4P':
          return {
            ext: 'm4p',
            mime: 'video/mp4'
          };
        case 'M4B':
          return {
            ext: 'm4b',
            mime: 'audio/mp4'
          };
        case 'M4A':
          return {
            ext: 'm4a',
            mime: 'audio/x-m4a'
          };
        case 'F4V':
          return {
            ext: 'f4v',
            mime: 'video/mp4'
          };
        case 'F4P':
          return {
            ext: 'f4p',
            mime: 'video/mp4'
          };
        case 'F4A':
          return {
            ext: 'f4a',
            mime: 'audio/mp4'
          };
        case 'F4B':
          return {
            ext: 'f4b',
            mime: 'audio/mp4'
          };
        case 'crx':
          return {
            ext: 'cr3',
            mime: 'image/x-canon-cr3'
          };
        default:
          if (brandMajor.startsWith('3g')) {
            if (brandMajor.startsWith('3g2')) {
              return {
                ext: '3g2',
                mime: 'video/3gpp2'
              };
            }
            return {
              ext: '3gp',
              mime: 'video/3gpp'
            };
          }
          return {
            ext: 'mp4',
            mime: 'video/mp4'
          };
      }
    }
    if (this.checkString('MThd')) {
      return {
        ext: 'mid',
        mime: 'audio/midi'
      };
    }
    if (this.checkString('wOFF') && (this.check([0x00, 0x01, 0x00, 0x00], {
      offset: 4
    }) || this.checkString('OTTO', {
      offset: 4
    }))) {
      return {
        ext: 'woff',
        mime: 'font/woff'
      };
    }
    if (this.checkString('wOF2') && (this.check([0x00, 0x01, 0x00, 0x00], {
      offset: 4
    }) || this.checkString('OTTO', {
      offset: 4
    }))) {
      return {
        ext: 'woff2',
        mime: 'font/woff2'
      };
    }
    if (this.check([0xD4, 0xC3, 0xB2, 0xA1]) || this.check([0xA1, 0xB2, 0xC3, 0xD4])) {
      return {
        ext: 'pcap',
        mime: 'application/vnd.tcpdump.pcap'
      };
    }

    // Sony DSD Stream File (DSF)
    if (this.checkString('DSD ')) {
      return {
        ext: 'dsf',
        mime: 'audio/x-dsf' // Non-standard
      };
    }
    if (this.checkString('LZIP')) {
      return {
        ext: 'lz',
        mime: 'application/x-lzip'
      };
    }
    if (this.checkString('fLaC')) {
      return {
        ext: 'flac',
        mime: 'audio/x-flac'
      };
    }
    if (this.check([0x42, 0x50, 0x47, 0xFB])) {
      return {
        ext: 'bpg',
        mime: 'image/bpg'
      };
    }
    if (this.checkString('wvpk')) {
      return {
        ext: 'wv',
        mime: 'audio/wavpack'
      };
    }
    if (this.checkString('%PDF')) {
      try {
        await tokenizer.ignore(1350);
        const maxBufferSize = 10 * 1024 * 1024;
        const buffer = new Uint8Array(Math.min(maxBufferSize, tokenizer.fileInfo.size));
        await tokenizer.readBuffer(buffer, {
          mayBeLess: true
        });

        // Check if this is an Adobe Illustrator file
        if (includes(buffer, new TextEncoder().encode('AIPrivateData'))) {
          return {
            ext: 'ai',
            mime: 'application/postscript'
          };
        }
      } catch (error) {
        // Swallow end of stream error if file is too small for the Adobe AI check
        if (!(error instanceof EndOfStreamError)) {
          throw error;
        }
      }

      // Assume this is just a normal PDF
      return {
        ext: 'pdf',
        mime: 'application/pdf'
      };
    }
    if (this.check([0x00, 0x61, 0x73, 0x6D])) {
      return {
        ext: 'wasm',
        mime: 'application/wasm'
      };
    }

    // TIFF, little-endian type
    if (this.check([0x49, 0x49])) {
      const fileType = await this.readTiffHeader(false);
      if (fileType) {
        return fileType;
      }
    }

    // TIFF, big-endian type
    if (this.check([0x4D, 0x4D])) {
      const fileType = await this.readTiffHeader(true);
      if (fileType) {
        return fileType;
      }
    }
    if (this.checkString('MAC ')) {
      return {
        ext: 'ape',
        mime: 'audio/ape'
      };
    }

    // https://github.com/file/file/blob/master/magic/Magdir/matroska
    if (this.check([0x1A, 0x45, 0xDF, 0xA3])) {
      // Root element: EBML
      async function readField() {
        const msb = await tokenizer.peekNumber(UINT8);
        let mask = 0x80;
        let ic = 0; // 0 = A, 1 = B, 2 = C, 3 = D

        while ((msb & mask) === 0 && mask !== 0) {
          ++ic;
          mask >>= 1;
        }
        const id = new Uint8Array(ic + 1);
        await tokenizer.readBuffer(id);
        return id;
      }
      async function readElement() {
        const idField = await readField();
        const lengthField = await readField();
        lengthField[0] ^= 0x80 >> lengthField.length - 1;
        const nrLength = Math.min(6, lengthField.length); // JavaScript can max read 6 bytes integer

        const idView = new DataView(idField.buffer);
        const lengthView = new DataView(lengthField.buffer, lengthField.length - nrLength, nrLength);
        return {
          id: getUintBE(idView),
          len: getUintBE(lengthView)
        };
      }
      async function readChildren(children) {
        while (children > 0) {
          const element = await readElement();
          if (element.id === 0x42_82) {
            const rawValue = await tokenizer.readToken(new StringType(element.len));
            return rawValue.replaceAll(/\00.*$/g, ''); // Return DocType
          }
          await tokenizer.ignore(element.len); // ignore payload
          --children;
        }
      }
      const re = await readElement();
      const docType = await readChildren(re.len);
      switch (docType) {
        case 'webm':
          return {
            ext: 'webm',
            mime: 'video/webm'
          };
        case 'matroska':
          return {
            ext: 'mkv',
            mime: 'video/x-matroska'
          };
        default:
          return;
      }
    }

    // RIFF file format which might be AVI, WAV, QCP, etc
    if (this.check([0x52, 0x49, 0x46, 0x46])) {
      if (this.check([0x41, 0x56, 0x49], {
        offset: 8
      })) {
        return {
          ext: 'avi',
          mime: 'video/vnd.avi'
        };
      }
      if (this.check([0x57, 0x41, 0x56, 0x45], {
        offset: 8
      })) {
        return {
          ext: 'wav',
          mime: 'audio/wav'
        };
      }

      // QLCM, QCP file
      if (this.check([0x51, 0x4C, 0x43, 0x4D], {
        offset: 8
      })) {
        return {
          ext: 'qcp',
          mime: 'audio/qcelp'
        };
      }
    }
    if (this.checkString('SQLi')) {
      return {
        ext: 'sqlite',
        mime: 'application/x-sqlite3'
      };
    }
    if (this.check([0x4E, 0x45, 0x53, 0x1A])) {
      return {
        ext: 'nes',
        mime: 'application/x-nintendo-nes-rom'
      };
    }
    if (this.checkString('Cr24')) {
      return {
        ext: 'crx',
        mime: 'application/x-google-chrome-extension'
      };
    }
    if (this.checkString('MSCF') || this.checkString('ISc(')) {
      return {
        ext: 'cab',
        mime: 'application/vnd.ms-cab-compressed'
      };
    }
    if (this.check([0xED, 0xAB, 0xEE, 0xDB])) {
      return {
        ext: 'rpm',
        mime: 'application/x-rpm'
      };
    }
    if (this.check([0xC5, 0xD0, 0xD3, 0xC6])) {
      return {
        ext: 'eps',
        mime: 'application/eps'
      };
    }
    if (this.check([0x28, 0xB5, 0x2F, 0xFD])) {
      return {
        ext: 'zst',
        mime: 'application/zstd'
      };
    }
    if (this.check([0x7F, 0x45, 0x4C, 0x46])) {
      return {
        ext: 'elf',
        mime: 'application/x-elf'
      };
    }
    if (this.check([0x21, 0x42, 0x44, 0x4E])) {
      return {
        ext: 'pst',
        mime: 'application/vnd.ms-outlook'
      };
    }
    if (this.checkString('PAR1')) {
      return {
        ext: 'parquet',
        mime: 'application/x-parquet'
      };
    }
    if (this.check([0xCF, 0xFA, 0xED, 0xFE])) {
      return {
        ext: 'macho',
        mime: 'application/x-mach-binary'
      };
    }

    // -- 5-byte signatures --

    if (this.check([0x4F, 0x54, 0x54, 0x4F, 0x00])) {
      return {
        ext: 'otf',
        mime: 'font/otf'
      };
    }
    if (this.checkString('#!AMR')) {
      return {
        ext: 'amr',
        mime: 'audio/amr'
      };
    }
    if (this.checkString('{\\rtf')) {
      return {
        ext: 'rtf',
        mime: 'application/rtf'
      };
    }
    if (this.check([0x46, 0x4C, 0x56, 0x01])) {
      return {
        ext: 'flv',
        mime: 'video/x-flv'
      };
    }
    if (this.checkString('IMPM')) {
      return {
        ext: 'it',
        mime: 'audio/x-it'
      };
    }
    if (this.checkString('-lh0-', {
      offset: 2
    }) || this.checkString('-lh1-', {
      offset: 2
    }) || this.checkString('-lh2-', {
      offset: 2
    }) || this.checkString('-lh3-', {
      offset: 2
    }) || this.checkString('-lh4-', {
      offset: 2
    }) || this.checkString('-lh5-', {
      offset: 2
    }) || this.checkString('-lh6-', {
      offset: 2
    }) || this.checkString('-lh7-', {
      offset: 2
    }) || this.checkString('-lzs-', {
      offset: 2
    }) || this.checkString('-lz4-', {
      offset: 2
    }) || this.checkString('-lz5-', {
      offset: 2
    }) || this.checkString('-lhd-', {
      offset: 2
    })) {
      return {
        ext: 'lzh',
        mime: 'application/x-lzh-compressed'
      };
    }

    // MPEG program stream (PS or MPEG-PS)
    if (this.check([0x00, 0x00, 0x01, 0xBA])) {
      //  MPEG-PS, MPEG-1 Part 1
      if (this.check([0x21], {
        offset: 4,
        mask: [0xF1]
      })) {
        return {
          ext: 'mpg',
          // May also be .ps, .mpeg
          mime: 'video/MP1S'
        };
      }

      // MPEG-PS, MPEG-2 Part 1
      if (this.check([0x44], {
        offset: 4,
        mask: [0xC4]
      })) {
        return {
          ext: 'mpg',
          // May also be .mpg, .m2p, .vob or .sub
          mime: 'video/MP2P'
        };
      }
    }
    if (this.checkString('ITSF')) {
      return {
        ext: 'chm',
        mime: 'application/vnd.ms-htmlhelp'
      };
    }
    if (this.check([0xCA, 0xFE, 0xBA, 0xBE])) {
      return {
        ext: 'class',
        mime: 'application/java-vm'
      };
    }

    // -- 6-byte signatures --

    if (this.check([0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00])) {
      return {
        ext: 'xz',
        mime: 'application/x-xz'
      };
    }
    if (this.checkString('<?xml ')) {
      return {
        ext: 'xml',
        mime: 'application/xml'
      };
    }
    if (this.check([0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C])) {
      return {
        ext: '7z',
        mime: 'application/x-7z-compressed'
      };
    }
    if (this.check([0x52, 0x61, 0x72, 0x21, 0x1A, 0x7]) && (this.buffer[6] === 0x0 || this.buffer[6] === 0x1)) {
      return {
        ext: 'rar',
        mime: 'application/x-rar-compressed'
      };
    }
    if (this.checkString('solid ')) {
      return {
        ext: 'stl',
        mime: 'model/stl'
      };
    }
    if (this.checkString('AC')) {
      const version = new StringType(4, 'latin1').get(this.buffer, 2);
      if (version.match('^d*') && version >= 1000 && version <= 1050) {
        return {
          ext: 'dwg',
          mime: 'image/vnd.dwg'
        };
      }
    }
    if (this.checkString('070707')) {
      return {
        ext: 'cpio',
        mime: 'application/x-cpio'
      };
    }

    // -- 7-byte signatures --

    if (this.checkString('BLENDER')) {
      return {
        ext: 'blend',
        mime: 'application/x-blender'
      };
    }
    if (this.checkString('!<arch>')) {
      await tokenizer.ignore(8);
      const string = await tokenizer.readToken(new StringType(13, 'ascii'));
      if (string === 'debian-binary') {
        return {
          ext: 'deb',
          mime: 'application/x-deb'
        };
      }
      return {
        ext: 'ar',
        mime: 'application/x-unix-archive'
      };
    }
    if (this.checkString('**ACE', {
      offset: 7
    })) {
      await tokenizer.peekBuffer(this.buffer, {
        length: 14,
        mayBeLess: true
      });
      if (this.checkString('**', {
        offset: 12
      })) {
        return {
          ext: 'ace',
          mime: 'application/x-ace-compressed'
        };
      }
    }

    // -- 8-byte signatures --

    if (this.check([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])) {
      // APNG format (https://wiki.mozilla.org/APNG_Specification)
      // 1. Find the first IDAT (image data) chunk (49 44 41 54)
      // 2. Check if there is an "acTL" chunk before the IDAT one (61 63 54 4C)

      // Offset calculated as follows:
      // - 8 bytes: PNG signature
      // - 4 (length) + 4 (chunk type) + 13 (chunk data) + 4 (CRC): IHDR chunk

      await tokenizer.ignore(8); // ignore PNG signature

      async function readChunkHeader() {
        return {
          length: await tokenizer.readToken(INT32_BE),
          type: await tokenizer.readToken(new StringType(4, 'latin1'))
        };
      }
      do {
        const chunk = await readChunkHeader();
        if (chunk.length < 0) {
          return; // Invalid chunk length
        }
        switch (chunk.type) {
          case 'IDAT':
            return {
              ext: 'png',
              mime: 'image/png'
            };
          case 'acTL':
            return {
              ext: 'apng',
              mime: 'image/apng'
            };
          default:
            await tokenizer.ignore(chunk.length + 4);
          // Ignore chunk-data + CRC
        }
      } while (tokenizer.position + 8 < tokenizer.fileInfo.size);
      return {
        ext: 'png',
        mime: 'image/png'
      };
    }
    if (this.check([0x41, 0x52, 0x52, 0x4F, 0x57, 0x31, 0x00, 0x00])) {
      return {
        ext: 'arrow',
        mime: 'application/x-apache-arrow'
      };
    }
    if (this.check([0x67, 0x6C, 0x54, 0x46, 0x02, 0x00, 0x00, 0x00])) {
      return {
        ext: 'glb',
        mime: 'model/gltf-binary'
      };
    }

    // `mov` format variants
    if (this.check([0x66, 0x72, 0x65, 0x65], {
      offset: 4
    }) // `free`
    || this.check([0x6D, 0x64, 0x61, 0x74], {
      offset: 4
    }) // `mdat` MJPEG
    || this.check([0x6D, 0x6F, 0x6F, 0x76], {
      offset: 4
    }) // `moov`
    || this.check([0x77, 0x69, 0x64, 0x65], {
      offset: 4
    }) // `wide`
    ) {
      return {
        ext: 'mov',
        mime: 'video/quicktime'
      };
    }

    // -- 9-byte signatures --

    if (this.check([0x49, 0x49, 0x52, 0x4F, 0x08, 0x00, 0x00, 0x00, 0x18])) {
      return {
        ext: 'orf',
        mime: 'image/x-olympus-orf'
      };
    }
    if (this.checkString('gimp xcf ')) {
      return {
        ext: 'xcf',
        mime: 'image/x-xcf'
      };
    }

    // -- 12-byte signatures --

    if (this.check([0x49, 0x49, 0x55, 0x00, 0x18, 0x00, 0x00, 0x00, 0x88, 0xE7, 0x74, 0xD8])) {
      return {
        ext: 'rw2',
        mime: 'image/x-panasonic-rw2'
      };
    }

    // ASF_Header_Object first 80 bytes
    if (this.check([0x30, 0x26, 0xB2, 0x75, 0x8E, 0x66, 0xCF, 0x11, 0xA6, 0xD9])) {
      async function readHeader() {
        const guid = new Uint8Array(16);
        await tokenizer.readBuffer(guid);
        return {
          id: guid,
          size: Number(await tokenizer.readToken(UINT64_LE))
        };
      }
      await tokenizer.ignore(30);
      // Search for header should be in first 1KB of file.
      while (tokenizer.position + 24 < tokenizer.fileInfo.size) {
        const header = await readHeader();
        let payload = header.size - 24;
        if (_check(header.id, [0x91, 0x07, 0xDC, 0xB7, 0xB7, 0xA9, 0xCF, 0x11, 0x8E, 0xE6, 0x00, 0xC0, 0x0C, 0x20, 0x53, 0x65])) {
          // Sync on Stream-Properties-Object (B7DC0791-A9B7-11CF-8EE6-00C00C205365)
          const typeId = new Uint8Array(16);
          payload -= await tokenizer.readBuffer(typeId);
          if (_check(typeId, [0x40, 0x9E, 0x69, 0xF8, 0x4D, 0x5B, 0xCF, 0x11, 0xA8, 0xFD, 0x00, 0x80, 0x5F, 0x5C, 0x44, 0x2B])) {
            // Found audio:
            return {
              ext: 'asf',
              mime: 'audio/x-ms-asf'
            };
          }
          if (_check(typeId, [0xC0, 0xEF, 0x19, 0xBC, 0x4D, 0x5B, 0xCF, 0x11, 0xA8, 0xFD, 0x00, 0x80, 0x5F, 0x5C, 0x44, 0x2B])) {
            // Found video:
            return {
              ext: 'asf',
              mime: 'video/x-ms-asf'
            };
          }
          break;
        }
        await tokenizer.ignore(payload);
      }

      // Default to ASF generic extension
      return {
        ext: 'asf',
        mime: 'application/vnd.ms-asf'
      };
    }
    if (this.check([0xAB, 0x4B, 0x54, 0x58, 0x20, 0x31, 0x31, 0xBB, 0x0D, 0x0A, 0x1A, 0x0A])) {
      return {
        ext: 'ktx',
        mime: 'image/ktx'
      };
    }
    if ((this.check([0x7E, 0x10, 0x04]) || this.check([0x7E, 0x18, 0x04])) && this.check([0x30, 0x4D, 0x49, 0x45], {
      offset: 4
    })) {
      return {
        ext: 'mie',
        mime: 'application/x-mie'
      };
    }
    if (this.check([0x27, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], {
      offset: 2
    })) {
      return {
        ext: 'shp',
        mime: 'application/x-esri-shape'
      };
    }
    if (this.check([0xFF, 0x4F, 0xFF, 0x51])) {
      return {
        ext: 'j2c',
        mime: 'image/j2c'
      };
    }
    if (this.check([0x00, 0x00, 0x00, 0x0C, 0x6A, 0x50, 0x20, 0x20, 0x0D, 0x0A, 0x87, 0x0A])) {
      // JPEG-2000 family

      await tokenizer.ignore(20);
      const type = await tokenizer.readToken(new StringType(4, 'ascii'));
      switch (type) {
        case 'jp2 ':
          return {
            ext: 'jp2',
            mime: 'image/jp2'
          };
        case 'jpx ':
          return {
            ext: 'jpx',
            mime: 'image/jpx'
          };
        case 'jpm ':
          return {
            ext: 'jpm',
            mime: 'image/jpm'
          };
        case 'mjp2':
          return {
            ext: 'mj2',
            mime: 'image/mj2'
          };
        default:
          return;
      }
    }
    if (this.check([0xFF, 0x0A]) || this.check([0x00, 0x00, 0x00, 0x0C, 0x4A, 0x58, 0x4C, 0x20, 0x0D, 0x0A, 0x87, 0x0A])) {
      return {
        ext: 'jxl',
        mime: 'image/jxl'
      };
    }
    if (this.check([0xFE, 0xFF])) {
      // UTF-16-BOM-LE
      if (this.check([0, 60, 0, 63, 0, 120, 0, 109, 0, 108], {
        offset: 2
      })) {
        return {
          ext: 'xml',
          mime: 'application/xml'
        };
      }
      return undefined; // Some unknown text based format
    }

    // -- Unsafe signatures --

    if (this.check([0x0, 0x0, 0x1, 0xBA]) || this.check([0x0, 0x0, 0x1, 0xB3])) {
      return {
        ext: 'mpg',
        mime: 'video/mpeg'
      };
    }
    if (this.check([0x00, 0x01, 0x00, 0x00, 0x00])) {
      return {
        ext: 'ttf',
        mime: 'font/ttf'
      };
    }
    if (this.check([0x00, 0x00, 0x01, 0x00])) {
      return {
        ext: 'ico',
        mime: 'image/x-icon'
      };
    }
    if (this.check([0x00, 0x00, 0x02, 0x00])) {
      return {
        ext: 'cur',
        mime: 'image/x-icon'
      };
    }
    if (this.check([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1])) {
      // Detected Microsoft Compound File Binary File (MS-CFB) Format.
      return {
        ext: 'cfb',
        mime: 'application/x-cfb'
      };
    }

    // Increase sample size from 12 to 256.
    await tokenizer.peekBuffer(this.buffer, {
      length: Math.min(256, tokenizer.fileInfo.size),
      mayBeLess: true
    });
    if (this.check([0x61, 0x63, 0x73, 0x70], {
      offset: 36
    })) {
      return {
        ext: 'icc',
        mime: 'application/vnd.iccprofile'
      };
    }

    // -- 15-byte signatures --

    if (this.checkString('BEGIN:')) {
      if (this.checkString('VCARD', {
        offset: 6
      })) {
        return {
          ext: 'vcf',
          mime: 'text/vcard'
        };
      }
      if (this.checkString('VCALENDAR', {
        offset: 6
      })) {
        return {
          ext: 'ics',
          mime: 'text/calendar'
        };
      }
    }

    // `raf` is here just to keep all the raw image detectors together.
    if (this.checkString('FUJIFILMCCD-RAW')) {
      return {
        ext: 'raf',
        mime: 'image/x-fujifilm-raf'
      };
    }
    if (this.checkString('Extended Module:')) {
      return {
        ext: 'xm',
        mime: 'audio/x-xm'
      };
    }
    if (this.checkString('Creative Voice File')) {
      return {
        ext: 'voc',
        mime: 'audio/x-voc'
      };
    }
    if (this.check([0x04, 0x00, 0x00, 0x00]) && this.buffer.length >= 16) {
      // Rough & quick check Pickle/ASAR
      const jsonSize = new DataView(this.buffer.buffer).getUint32(12, true);
      if (jsonSize > 12 && this.buffer.length >= jsonSize + 16) {
        try {
          const header = new TextDecoder().decode(this.buffer.slice(16, jsonSize + 16));
          const json = JSON.parse(header);
          // Check if Pickle is ASAR
          if (json.files) {
            // Final check, assuring Pickle/ASAR format
            return {
              ext: 'asar',
              mime: 'application/x-asar'
            };
          }
        } catch {}
      }
    }
    if (this.check([0x06, 0x0E, 0x2B, 0x34, 0x02, 0x05, 0x01, 0x01, 0x0D, 0x01, 0x02, 0x01, 0x01, 0x02])) {
      return {
        ext: 'mxf',
        mime: 'application/mxf'
      };
    }
    if (this.checkString('SCRM', {
      offset: 44
    })) {
      return {
        ext: 's3m',
        mime: 'audio/x-s3m'
      };
    }

    // Raw MPEG-2 transport stream (188-byte packets)
    if (this.check([0x47]) && this.check([0x47], {
      offset: 188
    })) {
      return {
        ext: 'mts',
        mime: 'video/mp2t'
      };
    }

    // Blu-ray Disc Audio-Video (BDAV) MPEG-2 transport stream has 4-byte TP_extra_header before each 188-byte packet
    if (this.check([0x47], {
      offset: 4
    }) && this.check([0x47], {
      offset: 196
    })) {
      return {
        ext: 'mts',
        mime: 'video/mp2t'
      };
    }
    if (this.check([0x42, 0x4F, 0x4F, 0x4B, 0x4D, 0x4F, 0x42, 0x49], {
      offset: 60
    })) {
      return {
        ext: 'mobi',
        mime: 'application/x-mobipocket-ebook'
      };
    }
    if (this.check([0x44, 0x49, 0x43, 0x4D], {
      offset: 128
    })) {
      return {
        ext: 'dcm',
        mime: 'application/dicom'
      };
    }
    if (this.check([0x4C, 0x00, 0x00, 0x00, 0x01, 0x14, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46])) {
      return {
        ext: 'lnk',
        mime: 'application/x.ms.shortcut' // Invented by us
      };
    }
    if (this.check([0x62, 0x6F, 0x6F, 0x6B, 0x00, 0x00, 0x00, 0x00, 0x6D, 0x61, 0x72, 0x6B, 0x00, 0x00, 0x00, 0x00])) {
      return {
        ext: 'alias',
        mime: 'application/x.apple.alias' // Invented by us
      };
    }
    if (this.checkString('Kaydara FBX Binary  \u0000')) {
      return {
        ext: 'fbx',
        mime: 'application/x.autodesk.fbx' // Invented by us
      };
    }
    if (this.check([0x4C, 0x50], {
      offset: 34
    }) && (this.check([0x00, 0x00, 0x01], {
      offset: 8
    }) || this.check([0x01, 0x00, 0x02], {
      offset: 8
    }) || this.check([0x02, 0x00, 0x02], {
      offset: 8
    }))) {
      return {
        ext: 'eot',
        mime: 'application/vnd.ms-fontobject'
      };
    }
    if (this.check([0x06, 0x06, 0xED, 0xF5, 0xD8, 0x1D, 0x46, 0xE5, 0xBD, 0x31, 0xEF, 0xE7, 0xFE, 0x74, 0xB7, 0x1D])) {
      return {
        ext: 'indd',
        mime: 'application/x-indesign'
      };
    }

    // Increase sample size from 256 to 512
    await tokenizer.peekBuffer(this.buffer, {
      length: Math.min(512, tokenizer.fileInfo.size),
      mayBeLess: true
    });

    // Requires a buffer size of 512 bytes
    if (tarHeaderChecksumMatches(this.buffer)) {
      return {
        ext: 'tar',
        mime: 'application/x-tar'
      };
    }
    if (this.check([0xFF, 0xFE])) {
      // UTF-16-BOM-BE
      if (this.check([60, 0, 63, 0, 120, 0, 109, 0, 108, 0], {
        offset: 2
      })) {
        return {
          ext: 'xml',
          mime: 'application/xml'
        };
      }
      if (this.check([0xFF, 0x0E, 0x53, 0x00, 0x6B, 0x00, 0x65, 0x00, 0x74, 0x00, 0x63, 0x00, 0x68, 0x00, 0x55, 0x00, 0x70, 0x00, 0x20, 0x00, 0x4D, 0x00, 0x6F, 0x00, 0x64, 0x00, 0x65, 0x00, 0x6C, 0x00], {
        offset: 2
      })) {
        return {
          ext: 'skp',
          mime: 'application/vnd.sketchup.skp'
        };
      }
      return undefined; // Some text based format
    }
    if (this.checkString('-----BEGIN PGP MESSAGE-----')) {
      return {
        ext: 'pgp',
        mime: 'application/pgp-encrypted'
      };
    }

    // Check MPEG 1 or 2 Layer 3 header, or 'layer 0' for ADTS (MPEG sync-word 0xFFE)
    if (this.buffer.length >= 2 && this.check([0xFF, 0xE0], {
      offset: 0,
      mask: [0xFF, 0xE0]
    })) {
      if (this.check([0x10], {
        offset: 1,
        mask: [0x16]
      })) {
        // Check for (ADTS) MPEG-2
        if (this.check([0x08], {
          offset: 1,
          mask: [0x08]
        })) {
          return {
            ext: 'aac',
            mime: 'audio/aac'
          };
        }

        // Must be (ADTS) MPEG-4
        return {
          ext: 'aac',
          mime: 'audio/aac'
        };
      }

      // MPEG 1 or 2 Layer 3 header
      // Check for MPEG layer 3
      if (this.check([0x02], {
        offset: 1,
        mask: [0x06]
      })) {
        return {
          ext: 'mp3',
          mime: 'audio/mpeg'
        };
      }

      // Check for MPEG layer 2
      if (this.check([0x04], {
        offset: 1,
        mask: [0x06]
      })) {
        return {
          ext: 'mp2',
          mime: 'audio/mpeg'
        };
      }

      // Check for MPEG layer 1
      if (this.check([0x06], {
        offset: 1,
        mask: [0x06]
      })) {
        return {
          ext: 'mp1',
          mime: 'audio/mpeg'
        };
      }
    }
  }
  async readTiffTag(bigEndian) {
    const tagId = await this.tokenizer.readToken(bigEndian ? UINT16_BE : UINT16_LE);
    this.tokenizer.ignore(10);
    switch (tagId) {
      case 50_341:
        return {
          ext: 'arw',
          mime: 'image/x-sony-arw'
        };
      case 50_706:
        return {
          ext: 'dng',
          mime: 'image/x-adobe-dng'
        };
    }
  }
  async readTiffIFD(bigEndian) {
    const numberOfTags = await this.tokenizer.readToken(bigEndian ? UINT16_BE : UINT16_LE);
    for (let n = 0; n < numberOfTags; ++n) {
      const fileType = await this.readTiffTag(bigEndian);
      if (fileType) {
        return fileType;
      }
    }
  }
  async readTiffHeader(bigEndian) {
    const version = (bigEndian ? UINT16_BE : UINT16_LE).get(this.buffer, 2);
    const ifdOffset = (bigEndian ? UINT32_BE : UINT32_LE).get(this.buffer, 4);
    if (version === 42) {
      // TIFF file header
      if (ifdOffset >= 6) {
        if (this.checkString('CR', {
          offset: 8
        })) {
          return {
            ext: 'cr2',
            mime: 'image/x-canon-cr2'
          };
        }
        if (ifdOffset >= 8 && (this.check([0x1C, 0x00, 0xFE, 0x00], {
          offset: 8
        }) || this.check([0x1F, 0x00, 0x0B, 0x00], {
          offset: 8
        }))) {
          return {
            ext: 'nef',
            mime: 'image/x-nikon-nef'
          };
        }
      }
      await this.tokenizer.ignore(ifdOffset);
      const fileType = await this.readTiffIFD(bigEndian);
      return fileType ?? {
        ext: 'tif',
        mime: 'image/tiff'
      };
    }
    if (version === 43) {
      // Big TIFF file header
      return {
        ext: 'tif',
        mime: 'image/tiff'
      };
    }
  }
}
new Set(extensions);
new Set(mimeTypes);

/**
Node.js specific entry point.
*/

class NodeFileTypeParser extends FileTypeParser {
  async fromStream(stream) {
    const tokenizer = await (stream instanceof ReadableStream ? fromWebStream(stream) : fromStream(stream));
    try {
      return super.fromTokenizer(tokenizer);
    } finally {
      await tokenizer.close();
    }
  }
  async fromFile(path) {
    const tokenizer = await fromFile(path);
    try {
      return await super.fromTokenizer(tokenizer);
    } finally {
      await tokenizer.close();
    }
  }
  async toDetectionStream(readableStream, options = {}) {
    if (readableStream instanceof ReadableStream) {
      return super.toDetectionStream(readableStream, options);
    }
    const {
      sampleSize = reasonableDetectionSizeInBytes
    } = options;
    return new Promise((resolve, reject) => {
      readableStream.on('error', reject);
      readableStream.once('readable', () => {
        (async () => {
          try {
            // Set up output stream
            const pass = new PassThrough();
            const outputStream = pipeline ? pipeline(readableStream, pass, () => {}) : readableStream.pipe(pass);

            // Read the input stream and detect the filetype
            const chunk = readableStream.read(sampleSize) ?? readableStream.read() ?? new Uint8Array(0);
            try {
              pass.fileType = await this.fromBuffer(chunk);
            } catch (error) {
              if (error instanceof EndOfStreamError) {
                pass.fileType = undefined;
              } else {
                reject(error);
              }
            }
            resolve(outputStream);
          } catch (error) {
            reject(error);
          }
        })();
      });
    });
  }
}
async function fileTypeFromFile(path, fileTypeOptions) {
  return new NodeFileTypeParser(fileTypeOptions).fromFile(path, fileTypeOptions);
}

const getNapCatDir = () => {
  const p = path__default.join(napCatCore.dataPath, "NapCat");
  fs$3.mkdirSync(p, {
    recursive: true
  });
  return p;
};
const getTempDir = () => {
  const p = path__default.join(getNapCatDir(), "temp");
  if (!fs$3.existsSync(p)) {
    fs$3.mkdirSync(p, {
      recursive: true
    });
  }
  return p;
};
function isGIF(path2) {
  const buffer = Buffer.alloc(4);
  const fd = fs$3.openSync(path2, "r");
  fs$3.readSync(fd, buffer, 0, 4, 0);
  fs$3.closeSync(fd);
  return buffer.toString() === "GIF8";
}
function checkFileReceived(path2, timeout = 3e3) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    function check() {
      if (fs$3.existsSync(path2)) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error(`文件不存在: ${path2}`));
      } else {
        setTimeout(check, 100);
      }
    }
    check();
  });
}
function calculateFileMD5(filePath) {
  return new Promise((resolve, reject) => {
    const stream = fs$3.createReadStream(filePath);
    const hash = crypto.createHash("md5");
    stream.on("data", (data) => {
      hash.update(data);
    });
    stream.on("end", () => {
      const md5 = hash.digest("hex");
      resolve(md5);
    });
    stream.on("error", (err) => {
      reject(err);
    });
  });
}
async function httpDownload(options) {
  let url;
  let headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
  };
  if (typeof options === "string") {
    url = options;
    const host = new URL(url).hostname;
    headers["Host"] = host;
  } else {
    url = options.url;
    if (options.headers) {
      if (typeof options.headers === "string") {
        headers = JSON.parse(options.headers);
      } else {
        headers = options.headers;
      }
    }
  }
  const fetchRes = await fetch(url, {
    headers
  }).catch((err) => {
    if (err.cause) {
      throw err.cause;
    }
    throw err;
  });
  if (!fetchRes.ok) throw new Error(`下载文件失败: ${fetchRes.statusText}`);
  const blob = await fetchRes.blob();
  const buffer = await blob.arrayBuffer();
  return Buffer.from(buffer);
}
async function uri2local(UriOrPath, fileName = null) {
  const res = {
    success: false,
    errMsg: "",
    fileName: "",
    ext: "",
    path: "",
    isLocal: false
  };
  if (!fileName) fileName = randomUUID();
  let filePath = path__default.join(getTempDir(), fileName);
  let url = null;
  try {
    if (fs$3.existsSync(UriOrPath)) url = new URL("file://" + UriOrPath);
  } catch (error) {
  }
  try {
    url = new URL(UriOrPath);
  } catch (error) {
  }
  if (!url) {
    res.errMsg = `UriOrPath ${UriOrPath} 解析失败,可能${UriOrPath}不存在`;
    return res;
  }
  if (url.protocol == "base64:") {
    const base64Data = UriOrPath.split("base64://")[1];
    try {
      const buffer = Buffer.from(base64Data, "base64");
      fs$3.writeFileSync(filePath, buffer);
    } catch (e) {
      res.errMsg = "base64文件下载失败," + e.toString();
      return res;
    }
  } else if (url.protocol == "http:" || url.protocol == "https:") {
    let buffer = null;
    try {
      buffer = await httpDownload(UriOrPath);
    } catch (e) {
      res.errMsg = `${url}下载失败,` + e.toString();
      return res;
    }
    try {
      const pathInfo = path__default.parse(decodeURIComponent(url.pathname));
      if (pathInfo.name) {
        fileName = pathInfo.name;
        if (pathInfo.ext) {
          fileName += pathInfo.ext;
        }
      }
      fileName = fileName.replace(/[/\\:*?"<>|]/g, "_");
      res.fileName = fileName;
      filePath = path__default.join(getTempDir(), randomUUID() + fileName);
      fs$3.writeFileSync(filePath, buffer);
    } catch (e) {
      res.errMsg = `${url}下载失败,` + e.toString();
      return res;
    }
  } else {
    let pathname;
    if (url.protocol === "file:") {
      pathname = decodeURIComponent(url.pathname);
      if (process.platform === "win32") {
        filePath = pathname.slice(1);
      } else {
        filePath = pathname;
      }
    }
    res.isLocal = true;
  }
  if (!res.isLocal && !res.ext) {
    try {
      const ext = (await fileTypeFromFile(filePath))?.ext;
      if (ext) {
        log("获取文件类型", ext, filePath);
        fs$3.renameSync(filePath, filePath + `.${ext}`);
        filePath += `.${ext}`;
        res.fileName += `.${ext}`;
        res.ext = ext;
      }
    } catch (e) {
    }
  }
  res.success = true;
  res.path = filePath;
  return res;
}

const defaultVideoThumbB64 = "/9j/4AAQSkZJRgABAQAAAQABAAD//gAXR2VuZXJhdGVkIGJ5IFNuaXBhc3Rl/9sAhAAKBwcIBwYKCAgICwoKCw4YEA4NDQ4dFRYRGCMfJSQiHyIhJis3LyYpNCkhIjBBMTQ5Oz4+PiUuRElDPEg3PT47AQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAF/APADAREAAhEBAxEB/8QBogAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoLEAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+foBAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKCxEAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDiAayNxwagBwNAC5oAM0xBmgBM0ANJoAjY0AQsaBkTGgCM0DEpAFAC0AFMBaACgAoEJTASgQlACUwCgQ4UAOFADhQA4UAOFADxQIkBqDQUGgBwagBQaBC5pgGaAELUAMLUARs1AETGgBhNAxhoASkAUALQIKYxaBBQAUwEoAQ0CEoASmAUAOoEKKAHCgBwoAeKAHigQ7NZmoZpgLmgBd1Ahd1ABupgNLUAMLUAMY0AMJoAYaAENACUCCgAoAWgAoAWgBKYCUAJQISgApgLQAooEOFACigB4oAeKBDxQAVmaiZpgGaAFzQAbqAE3UAIWpgNJoAYTQIaaAEoAQ0CEoASgBaACgBaACmAUAJQAlAgoAKYC0AKKBCigB4FADgKBDwKAHigBuazNRM0DEzTAM0AJmgAzQAhNAhpNACGmA2gQlACUCEoAKACgBaAFpgFACUAJQAUCCmAUALQIcBQA4CgB4FADgKBDhQA4UAMzWZqNzTGJQAZoATNABmgBKAEoEIaYCUCEoASgQlABQAtABQAtMBKACgAoEFABimAYoEKBQA4CgB4FADwKBDgKAFFADhQBCazNhKAEpgFACUAFACUAFAhDTAbQISgAoEJQAUALQAtMAoAKADFABigQYoAMUALimIUCgBwFAh4FADgKAHUALQAtAENZmwlACUwEoAKAEoAKACgQlMBpoEJQAUCCgBcUAFABTAXFAC4oAMUAGKBBigAxQIKYCigQ8UAOFADhQAtAC0ALQBDWZqJQMSgBKYBQAlABQISgBKYCGgQlAC0CCgBcUAFABTAUCkA7FMAxQAYoEJQAUCCmAooEOFADxQA4UAFAC0ALQBDWZqJQAlACUxhQAlABQIKAEoASmISgBcUCCgBaACgBcUAKBQAuKYC0CEoAQ0AJQISmAooEPFADhQA4UALQAtAC0AQ1maiUAFACUAJTAKAEoAKAEoAMUxBigAxQIWgAoAKAFAoAWgBaYBQIQ0ANNACUCCmIUUAOFADxQA4UALQAtABQBFWZqFACUAFACYpgFACUAFACUAFAgxTEFABQAUALQAooAWgAoAKYDTQIaaAEpiCgQ4UAOFAh4oGOFAC0ALSAKYEdZmglABQAUDDFACUwEoASgAoAKBBQIKYBQAUALQAtAC0AJQAhpgNJoENJoATNMQCgQ8UCHigB4oAWgYtABQAUAMrM0CgAoAKADFACUxiUAJQAlAgoAKYgoAKACgYtAC0AFAhDTAQmgBhNAhpNACZpiFBoEPFAEi0CHigB1ABQAUDEoAbWZoFABQAtABTAQ0ANNAxDQAlAhaAEpiCgAoGFAC0AFABmgBCaYhpNADCaBDSaBBmgABpiJFNAEimgB4NADqAFzQAlACE0AJWZoFAC0AFAC0wEIoAaaAG0AJQAUCCgApjCgAoAKADNABmgBpNMQ0mgBpNAhhNAgzQAoNADwaAHqaAJAaBDgaYC5oATNACZoAWszQKACgBaBDqYCGgBpoAYaBiUCCgBKYBQMKACgAoAM0AITQIaTQA0mmA0mgQ3NAhKAHCgBwNADwaAHg0AOBpiFzQAZoATNAD6zNAoAKAFoEOpgBoAaaAGGmAw0AJmgAzQMM0AGaADNABmgBM0AITQIaTQAhNMQw0AJQIKAFFADhQA4GgBwNADs0xC5oAM0CDNAEtZmoUCCgBaAHUwCgBppgRtQAw0ANzQAZoAM0AGaADNABmgBKAEoAQ0ANNMQhoEJQAlMBaQDgaAFBoAcDTAdmgQuaADNAgzQBPWZqFAgoAWgBaYC0CGmmBG1AyM0ANJoATNACZoAXNABmgAzQAUAJQAhoAQ0xDTQISmAUALQAUgHA0AKDTAdmgQuaBBQAtAFiszQKACgBaAFFMAoEIaYEbUDI2oAYaAEoASgAzQAuaACgAoAKAENMQ00AJTEFAhKACgAoAXNACg0AOBoAWgQtAC0AWazNAoAKACgBaYBQIQ0AMNMYw0AMIoAbQAlMAoAKACgAzSAKYhKAENACUxBQIKACgBKACgBaAHCgQ4UALQAUAWqzNAoAKACgApgFACGgQ00xjTQAwigBCKAG4pgJQAlABQAUCCgBKACgBKYgoEFABQISgAoAWgBRQA4UALQAUCLdZmoUAFABQAlMAoASgBDQA00wENACYoATFMBpFADSKAEoEJQAUAFABQAlMQtAgoASgQUAJQAUAKKAHCgBaBBQBbrM1CgAoAKACmAUAJQAlADaYBQAlACYpgIRQA0igBpFAhtABQAUAFMAoEFABQIKAEoASgQUALQAooAWgQUAW81mbC0CCgApgFACUAIaAEpgJQAUAFABQAhFMBpFADSKAGkUCExQAYoAMUAGKADFMQYoAMUCExSATFABQIKYBQAtABQIt5qDYM0ALmgQtIApgIaAENADaACmAlAC0ALQAUwGkUANIoAaRQAmKBBigAxQAYoAMUAGKBBigBMUAJigQmKAExTAKBC0AFAFnNQaig0AKDQAtAgoASgBDQAlMBKACgAFADhQAtMBCKAGkUAIRQAmKADFABigQmKADFACYoAXFABigQmKAExQAmKBCYpgJigAoAnzUGgZoAcDQAuaBC0AJQAhoASmAlABQAtADhQAtMAoATFACEUAJigAxQAYoATFAhMUAFABQAuKADFABigBpWgBCKBCYpgJigB+ag0DNADgaBDgaAFzQITNACUAJTAKACgBRQAopgOoAWgBKAEoAKACgAoASgBpoEJQAooAWgBaBhigBMUCEIoAQigBMUAJSLCgBQaBDgaQC5oEFACUwCgBKACmAtADhQA4UALQAUAJQAUAJQAUAJQAhoENoAWgBRQAooGLQAUAGKAGkUAIRQIZSKEoGKKBDhQAUCCgAoAKBBQAUwFoGKKAHCgBaACgAoASgAoASgBCaAEoEJmgAoAUGgBQaAHZoGFABQAUANoAjpDEoAWgBaAFoEFACUALQAUCCmAUAOFAxRQAtAC0AJQAUAJQAmaBDSaAEzQAmaYBmgBQaAHA0gFzQAuaBhmgAzQAlAEdIYUALQAtAgoAKAEoEFAC0AFMAoAUUDFFAC0ALQAUAJQAhoENNACE0wEoATNABmgBc0ALmgBc0gDNAC5oATNABmgBKRQlACigB1AgoASgQlABTAWgBKACgBaBi0ALQAZoAM0AFACGgQ00wENACUAJQAUCFzQMM0ALmgAzQAZoAM0AGaQC0igoAUUALQIWgBDQISmAUAFACUAFABQAuaBi5oAM0AGaBBmgBKAEpgIaAG0AJQAUCFoAM0DDNAC5oATNABmgAzQBJUlBQAooAWgQtACGmIaaACgAoASgBKACgBc0DCgQUAGaADNABTASgBDQAlACUAFAgoAKBhQAUAFABQAlAE1SUFAxRQIWgQtMBDQIQ0AJQAlAhKBiUAFABmgBc0AGaADNABTAKACgBKAEoASgQlABQAUAFAC0AFACUAFAE1SaBQAUCHCgQtMBKBCUAJQISgBDQA00DEzQAuaADNMBc0AGaADNABQAUAJQAlABQISgAoAKACgBaACgBKAEoAnqTQSgBRQIcKBC0xCUAJQISgBKAENADDQAmaYwzQAuaADNAC0AFABQAUAFAhKACgBKACgAoAWgAoELQAlAxKAJqk0EoAWgQooELTEFADaBCUABoENNMY00ANNAwzQAZoAXNAC0AFAC0CFoASgAoASgBKACgAoAWgQtABQAUANNAyWpNAoAKBCimIWgQUCEoASmIQ0ANNADTQMaaAEoGLmgAzQAtADhQIWgBaACgQhoASgYlACUALQIWgBaACgBKAENAyWpNBKYBQIcKBC0CEoEJTAKBCUANNADDQMQ0ANoGFAC5oAUGgBwNAhRQIWgBaAENACGgBtAwoAKAFzQIXNABmgAoAQ0DJKRoJQAtAhRQSLQIKYCUCCgBDQA00AMNAxpoGNoAM0AGaAFBoAcDQIcKBDqACgBDQAhoAQ0DEoAKADNAC5oEGaBhmgAoAkpGgUCCgQooELQIKYhKACgBKAGmgBpoGMNAxDQAlAwzQIUUAOFAhwoAcKBC0AJQAhoGNNACUAFABQAZoAXNABQAUAS0ixKACgQoNAhaYgoEFACUABoAaaAGmgYw0DENAxtABQAooEOFADhQIcKAFoASgBDQAhoGJQAUAFACUALQIKBi0CJDSLEoATNAhc0CHZpiCgQUAJQIKBjTQAhoGNNAxpoATFABigBQKAHCgBwoAWgAoAKACgBKAEoASgAoASgBaAAUAOoEONIoaTQAZoAUGmIUGgQtAgzQISgAoAQ0DGmgYlAxKACgAxQAtACigBRQAtAxaACgAoATFABigBCKAG0CEoAWgBRTAUUAf//Z";
const defaultVideoThumb = Buffer.from(defaultVideoThumbB64, "base64");
async function getVideoInfo(filePath) {
  const size = fs$3.statSync(filePath).size;
  return new Promise((resolve, reject) => {
    const ffmpegPath = process.env.FFMPEG_PATH;
    ffmpegPath && ffmpeg.setFfmpegPath(ffmpegPath);
    ffmpeg(filePath).ffprobe((err, metadata) => {
      if (err) {
        reject(err);
      } else {
        const videoStream = metadata.streams.find((s) => s.codec_type === "video");
        if (videoStream) {
          log(`视频尺寸: ${videoStream.width}x${videoStream.height}`);
        } else {
          return reject("未找到视频流信息。");
        }
        resolve({
          width: videoStream.width,
          height: videoStream.height,
          time: parseInt(videoStream.duration),
          format: metadata.format.format_name,
          size,
          filePath
        });
      }
    });
  });
}

let TEMP_DIR = "./";
setTimeout(() => {
  TEMP_DIR = getTempDir();
}, 100);
async function encodeSilk(filePath) {
  async function guessDuration(pttPath) {
    const pttFileInfo = await fsPromise.stat(pttPath);
    let duration = pttFileInfo.size / 1024 / 3;
    duration = Math.floor(duration);
    duration = Math.max(1, duration);
    log("通过文件大小估算语音的时长:", duration);
    return duration;
  }
  try {
    const file = await fsPromise.readFile(filePath);
    const pttPath = path__default.join(TEMP_DIR, randomUUID());
    if (!isSilk(file)) {
      log(`语音文件${filePath}需要转换成silk`);
      const _isWav = isWav(file);
      const pcmPath = pttPath + ".pcm";
      let sampleRate = 0;
      const convert = () => {
        return new Promise((resolve, reject) => {
          const ffmpegPath = process.env.FFMPEG_PATH || "ffmpeg";
          const cp = spawn(ffmpegPath, ["-y", "-i", filePath, "-ar", "24000", "-ac", "1", "-f", "s16le", pcmPath]);
          cp.on("error", (err) => {
            log("FFmpeg处理转换出错: ", err.message);
            return reject(err);
          });
          cp.on("exit", (code, signal) => {
            const EXIT_CODES = [0, 255];
            if (code == null || EXIT_CODES.includes(code)) {
              sampleRate = 24e3;
              const data = fs$3.readFileSync(pcmPath);
              fs$3.unlink(pcmPath, (err) => {
              });
              return resolve(data);
            }
            log(`FFmpeg exit: code=${code ?? "unknown"} sig=${signal ?? "unknown"}`);
            reject(Error("FFmpeg处理转换失败"));
          });
        });
      };
      let input;
      if (!_isWav) {
        input = await convert();
      } else {
        input = file;
        const allowSampleRate = [8e3, 12e3, 16e3, 24e3, 32e3, 44100, 48e3];
        const {
          fmt
        } = getWavFileInfo(input);
        if (!allowSampleRate.includes(fmt.sampleRate)) {
          input = await convert();
        }
      }
      const silk = await encode(input, sampleRate);
      fs$3.writeFileSync(pttPath, silk.data);
      log(`语音文件${filePath}转换成功!`, pttPath, "时长:", silk.duration);
      return {
        converted: true,
        path: pttPath,
        duration: silk.duration / 1e3
      };
    } else {
      const silk = file;
      let duration = 0;
      try {
        duration = getDuration(silk) / 1e3;
      } catch (e) {
        log("获取语音文件时长失败, 使用文件大小推测时长", filePath, e.stack);
        duration = await guessDuration(filePath);
      }
      return {
        converted: false,
        path: filePath,
        duration
      };
    }
  } catch (error) {
    logError("convert silk failed", error.stack);
    return {};
  }
}

const sysface = [
	{
		QSid: "392",
		QDes: "/龙年快乐",
		IQLid: "392",
		AQLid: "392",
		EMCode: "10392",
		AniStickerType: 3,
		AniStickerPackId: "1",
		AniStickerId: "38"
	},
	{
		QSid: "393",
		QDes: "/新年中龙",
		IQLid: "393",
		AQLid: "393",
		EMCode: "10393",
		QHide: "1",
		AniStickerType: 3,
		AniStickerPackId: "1",
		AniStickerId: "39"
	},
	{
		QSid: "364",
		QDes: "/超级赞",
		IQLid: "364",
		AQLid: "364",
		EMCode: "10364",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "1",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "366",
		QDes: "/芒狗",
		IQLid: "366",
		AQLid: "366",
		EMCode: "10366",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "2",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "362",
		QDes: "/好兄弟",
		IQLid: "362",
		AQLid: "362",
		EMCode: "10362",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "3",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "397",
		QDes: "/抛媚眼",
		IQLid: "397",
		AQLid: "397",
		EMCode: "10397",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "4",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "396",
		QDes: "/狼狗",
		IQLid: "396",
		AQLid: "396",
		EMCode: "10396",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "5",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "360",
		QDes: "/亲亲",
		IQLid: "360",
		AQLid: "360",
		EMCode: "10360",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "6",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "361",
		QDes: "/狗狗笑哭",
		IQLid: "361",
		AQLid: "361",
		EMCode: "10361",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "7",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "363",
		QDes: "/狗狗可怜",
		IQLid: "363",
		AQLid: "363",
		EMCode: "10363",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "8",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "365",
		QDes: "/狗狗生气",
		IQLid: "365",
		AQLid: "365",
		EMCode: "10365",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "9",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "367",
		QDes: "/狗狗疑问",
		IQLid: "367",
		AQLid: "367",
		EMCode: "10367",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "10",
		AniStickerPackId: "2",
		AniStickerPackName: "汪汪"
	},
	{
		QSid: "399",
		QDes: "/tui",
		IQLid: "399",
		AQLid: "399",
		EMCode: "10399",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "1",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "398",
		QDes: "/超级ok",
		IQLid: "398",
		AQLid: "398",
		EMCode: "10398",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "2",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "373",
		QDes: "/忙",
		IQLid: "373",
		AQLid: "373",
		EMCode: "10373",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "3",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "370",
		QDes: "/祝贺",
		IQLid: "370",
		AQLid: "370",
		EMCode: "10370",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "4",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "375",
		QDes: "/超级鼓掌",
		IQLid: "375",
		AQLid: "375",
		EMCode: "10375",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "5",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "368",
		QDes: "/奥特笑哭",
		IQLid: "368",
		AQLid: "368",
		EMCode: "10368",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "6",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "369",
		QDes: "/彩虹",
		IQLid: "369",
		AQLid: "369",
		EMCode: "10369",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "7",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "371",
		QDes: "/冒泡",
		IQLid: "371",
		AQLid: "371",
		EMCode: "10371",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "8",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "372",
		QDes: "/气呼呼",
		IQLid: "372",
		AQLid: "372",
		EMCode: "10372",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "9",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "374",
		QDes: "/波波流泪",
		IQLid: "374",
		AQLid: "374",
		EMCode: "10374",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "10",
		AniStickerPackId: "6",
		AniStickerPackName: "噗噗星人"
	},
	{
		QSid: "382",
		QDes: "/emo",
		IQLid: "382",
		AQLid: "382",
		EMCode: "10382",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "1",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "383",
		QDes: "/企鹅爱心",
		IQLid: "383",
		AQLid: "383",
		EMCode: "10383",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "2",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "401",
		QDes: "/超级转圈",
		IQLid: "401",
		AQLid: "401",
		EMCode: "10401",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "3",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "400",
		QDes: "/快乐",
		IQLid: "400",
		AQLid: "400",
		EMCode: "10400",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "4",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "380",
		QDes: "/真棒",
		IQLid: "380",
		AQLid: "380",
		EMCode: "10380",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "5",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "381",
		QDes: "/路过",
		IQLid: "381",
		AQLid: "381",
		EMCode: "10381",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "6",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "379",
		QDes: "/企鹅流泪",
		IQLid: "379",
		AQLid: "379",
		EMCode: "10379",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "7",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "376",
		QDes: "/跺脚",
		IQLid: "376",
		AQLid: "376",
		EMCode: "10376",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "8",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "378",
		QDes: "/企鹅笑哭",
		IQLid: "378",
		AQLid: "378",
		EMCode: "10378",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "9",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "377",
		QDes: "/嗨",
		IQLid: "377",
		AQLid: "377",
		EMCode: "10377",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "10",
		AniStickerPackId: "5",
		AniStickerPackName: "企鹅"
	},
	{
		QSid: "403",
		QDes: "/出去玩",
		IQLid: "403",
		AQLid: "403",
		EMCode: "10403",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "1",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "402",
		QDes: "/别说话",
		IQLid: "402",
		AQLid: "402",
		EMCode: "10402",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "2",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "390",
		QDes: "/太头秃",
		IQLid: "390",
		AQLid: "390",
		EMCode: "10390",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "3",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "391",
		QDes: "/太沧桑",
		IQLid: "391",
		AQLid: "391",
		EMCode: "10391",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "4",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "388",
		QDes: "/太头疼",
		IQLid: "388",
		AQLid: "388",
		EMCode: "10388",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "5",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "389",
		QDes: "/太赞了",
		IQLid: "389",
		AQLid: "389",
		EMCode: "10389",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "6",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "386",
		QDes: "/呜呜呜",
		IQLid: "386",
		AQLid: "386",
		EMCode: "10386",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "7",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "385",
		QDes: "/太气了",
		IQLid: "385",
		AQLid: "385",
		EMCode: "10385",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "8",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "384",
		QDes: "/晚安",
		IQLid: "384",
		AQLid: "384",
		EMCode: "10384",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "9",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "387",
		QDes: "/太好笑",
		IQLid: "387",
		AQLid: "387",
		EMCode: "10387",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "10",
		AniStickerPackId: "4",
		AniStickerPackName: "QQ黄脸"
	},
	{
		QSid: "413",
		QDes: "/摇起来",
		IQLid: "413",
		AQLid: "413",
		EMCode: "10413",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "1",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "405",
		QDes: "/好运来",
		IQLid: "405",
		AQLid: "405",
		EMCode: "10405",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "2",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "404",
		QDes: "/闪亮登场",
		IQLid: "404",
		AQLid: "404",
		EMCode: "10404",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "3",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "406",
		QDes: "/姐是女王",
		IQLid: "406",
		AQLid: "406",
		EMCode: "10406",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "4",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "410",
		QDes: "/么么哒",
		IQLid: "410",
		AQLid: "410",
		EMCode: "10410",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "5",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "411",
		QDes: "/一起嗨",
		IQLid: "411",
		AQLid: "411",
		EMCode: "10411",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "6",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "407",
		QDes: "/我听听",
		IQLid: "407",
		AQLid: "407",
		EMCode: "10407",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "7",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "408",
		QDes: "/臭美",
		IQLid: "408",
		AQLid: "408",
		EMCode: "10408",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "8",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "412",
		QDes: "/开心",
		IQLid: "412",
		AQLid: "412",
		EMCode: "10412",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "9",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "409",
		QDes: "/送你花花",
		IQLid: "409",
		AQLid: "409",
		EMCode: "10409",
		QHide: "1",
		AniStickerType: 1,
		AniStickerId: "10",
		AniStickerPackId: "3",
		AniStickerPackName: "喜花妮"
	},
	{
		QSid: "394",
		QDes: "/新年大龙",
		IQLid: "394",
		AQLid: "394",
		EMCode: "10394",
		QHide: "1",
		AniStickerType: 3,
		AniStickerPackId: "1",
		AniStickerId: "40"
	},
	{
		QSid: "14",
		QDes: "/微笑",
		IQLid: "23",
		AQLid: "23",
		EMCode: "100"
	},
	{
		QSid: "1",
		QDes: "/撇嘴",
		IQLid: "40",
		AQLid: "40",
		EMCode: "101"
	},
	{
		QSid: "2",
		QDes: "/色",
		IQLid: "19",
		AQLid: "19",
		EMCode: "102"
	},
	{
		QSid: "3",
		QDes: "/发呆",
		IQLid: "43",
		AQLid: "43",
		EMCode: "103"
	},
	{
		QSid: "4",
		QDes: "/得意",
		IQLid: "21",
		AQLid: "21",
		EMCode: "104"
	},
	{
		QSid: "6",
		QDes: "/害羞",
		IQLid: "20",
		AQLid: "20",
		EMCode: "106"
	},
	{
		QSid: "7",
		QDes: "/闭嘴",
		IQLid: "104",
		AQLid: "106",
		EMCode: "107"
	},
	{
		QSid: "8",
		QDes: "/睡",
		IQLid: "35",
		AQLid: "35",
		EMCode: "108"
	},
	{
		QSid: "9",
		QDes: "/大哭",
		IQLid: "10",
		AQLid: "10",
		EMCode: "109"
	},
	{
		QSid: "5",
		QDes: "/流泪",
		IQLid: "9",
		AQLid: "9",
		EMCode: "105",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "16"
	},
	{
		QSid: "10",
		QDes: "/尴尬",
		IQLid: "25",
		AQLid: "25",
		EMCode: "110"
	},
	{
		QSid: "11",
		QDes: "/发怒",
		IQLid: "24",
		AQLid: "24",
		EMCode: "111"
	},
	{
		QSid: "12",
		QDes: "/调皮",
		IQLid: "1",
		AQLid: "1",
		EMCode: "112"
	},
	{
		QSid: "13",
		QDes: "/呲牙",
		IQLid: "0",
		AQLid: "0",
		EMCode: "113"
	},
	{
		QSid: "0",
		QDes: "/惊讶",
		IQLid: "33",
		AQLid: "33",
		EMCode: "114"
	},
	{
		QSid: "15",
		QDes: "/难过",
		IQLid: "32",
		AQLid: "32",
		EMCode: "115"
	},
	{
		QSid: "16",
		QDes: "/酷",
		IQLid: "12",
		AQLid: "12",
		EMCode: "116"
	},
	{
		QSid: "96",
		QDes: "/冷汗",
		IQLid: "27",
		AQLid: "27",
		EMCode: "117"
	},
	{
		QSid: "18",
		QDes: "/抓狂",
		IQLid: "13",
		AQLid: "13",
		EMCode: "118"
	},
	{
		QSid: "19",
		QDes: "/吐",
		IQLid: "22",
		AQLid: "22",
		EMCode: "119"
	},
	{
		QSid: "20",
		QDes: "/偷笑",
		IQLid: "3",
		AQLid: "3",
		EMCode: "120"
	},
	{
		QSid: "21",
		QDes: "/可爱",
		IQLid: "18",
		AQLid: "18",
		EMCode: "121"
	},
	{
		QSid: "22",
		QDes: "/白眼",
		IQLid: "30",
		AQLid: "30",
		EMCode: "122"
	},
	{
		QSid: "23",
		QDes: "/傲慢",
		IQLid: "31",
		AQLid: "31",
		EMCode: "123"
	},
	{
		QSid: "24",
		QDes: "/饥饿",
		IQLid: "79",
		AQLid: "81",
		EMCode: "124"
	},
	{
		QSid: "25",
		QDes: "/困",
		IQLid: "80",
		AQLid: "82",
		EMCode: "125"
	},
	{
		QSid: "26",
		QDes: "/惊恐",
		IQLid: "26",
		AQLid: "26",
		EMCode: "126"
	},
	{
		QSid: "27",
		QDes: "/流汗",
		IQLid: "2",
		AQLid: "2",
		EMCode: "127"
	},
	{
		QSid: "28",
		QDes: "/憨笑",
		IQLid: "37",
		AQLid: "37",
		EMCode: "128"
	},
	{
		QSid: "29",
		QDes: "/悠闲",
		IQLid: "50",
		AQLid: "50",
		EMCode: "129"
	},
	{
		QSid: "30",
		QDes: "/奋斗",
		IQLid: "42",
		AQLid: "42",
		EMCode: "130"
	},
	{
		QSid: "31",
		QDes: "/咒骂",
		IQLid: "81",
		AQLid: "83",
		EMCode: "131"
	},
	{
		QSid: "32",
		QDes: "/疑问",
		IQLid: "34",
		AQLid: "34",
		EMCode: "132"
	},
	{
		QSid: "33",
		QDes: "/嘘",
		IQLid: "11",
		AQLid: "11",
		EMCode: "133"
	},
	{
		QSid: "34",
		QDes: "/晕",
		IQLid: "49",
		AQLid: "49",
		EMCode: "134"
	},
	{
		QSid: "35",
		QDes: "/折磨",
		IQLid: "82",
		AQLid: "84",
		EMCode: "135"
	},
	{
		QSid: "36",
		QDes: "/衰",
		IQLid: "39",
		AQLid: "39",
		EMCode: "136"
	},
	{
		QSid: "37",
		QDes: "/骷髅",
		isStatic: "1",
		IQLid: "76",
		AQLid: "78",
		EMCode: "137"
	},
	{
		QSid: "38",
		QDes: "/敲打",
		IQLid: "5",
		AQLid: "5",
		EMCode: "138"
	},
	{
		QSid: "39",
		QDes: "/再见",
		IQLid: "4",
		AQLid: "4",
		EMCode: "139"
	},
	{
		QSid: "97",
		QDes: "/擦汗",
		IQLid: "6",
		AQLid: "6",
		EMCode: "140"
	},
	{
		QSid: "98",
		QDes: "/抠鼻",
		IQLid: "83",
		AQLid: "85",
		EMCode: "141"
	},
	{
		QSid: "99",
		QDes: "/鼓掌",
		IQLid: "84",
		AQLid: "86",
		EMCode: "142"
	},
	{
		QSid: "100",
		QDes: "/糗大了",
		IQLid: "85",
		AQLid: "87",
		EMCode: "143"
	},
	{
		QSid: "101",
		QDes: "/坏笑",
		IQLid: "46",
		AQLid: "46",
		EMCode: "144"
	},
	{
		QSid: "102",
		QDes: "/左哼哼",
		IQLid: "86",
		AQLid: "88",
		EMCode: "145"
	},
	{
		QSid: "103",
		QDes: "/右哼哼",
		IQLid: "44",
		AQLid: "44",
		EMCode: "146"
	},
	{
		QSid: "104",
		QDes: "/哈欠",
		IQLid: "87",
		AQLid: "89",
		EMCode: "147"
	},
	{
		QSid: "105",
		QDes: "/鄙视",
		IQLid: "48",
		AQLid: "48",
		EMCode: "148"
	},
	{
		QSid: "106",
		QDes: "/委屈",
		IQLid: "14",
		AQLid: "14",
		EMCode: "149"
	},
	{
		QSid: "107",
		QDes: "/快哭了",
		IQLid: "88",
		AQLid: "90",
		EMCode: "150"
	},
	{
		QSid: "108",
		QDes: "/阴险",
		IQLid: "41",
		AQLid: "41",
		EMCode: "151"
	},
	{
		QSid: "305",
		QDes: "/右亲亲",
		IQLid: "305",
		AQLid: "305",
		EMCode: "10305"
	},
	{
		QSid: "109",
		QDes: "/左亲亲",
		IQLid: "36",
		AQLid: "36",
		EMCode: "152"
	},
	{
		QSid: "110",
		QDes: "/吓",
		IQLid: "89",
		AQLid: "91",
		EMCode: "153"
	},
	{
		QSid: "111",
		QDes: "/可怜",
		IQLid: "51",
		AQLid: "51",
		EMCode: "154"
	},
	{
		QSid: "172",
		QDes: "/眨眼睛",
		IQLid: "142",
		AQLid: "164",
		EMCode: "242"
	},
	{
		QSid: "182",
		QDes: "/笑哭",
		IQLid: "152",
		AQLid: "174",
		EMCode: "252"
	},
	{
		QSid: "179",
		QDes: "/doge",
		IQLid: "149",
		AQLid: "171",
		EMCode: "249"
	},
	{
		QSid: "173",
		QDes: "/泪奔",
		IQLid: "143",
		AQLid: "165",
		EMCode: "243"
	},
	{
		QSid: "174",
		QDes: "/无奈",
		IQLid: "144",
		AQLid: "166",
		EMCode: "244"
	},
	{
		QSid: "212",
		QDes: "/托腮",
		IQLid: "182",
		AQLid: "161",
		EMCode: "282"
	},
	{
		QSid: "175",
		QDes: "/卖萌",
		IQLid: "145",
		AQLid: "167",
		EMCode: "245"
	},
	{
		QSid: "178",
		QDes: "/斜眼笑",
		IQLid: "148",
		AQLid: "170",
		EMCode: "248"
	},
	{
		QSid: "177",
		QDes: "/喷血",
		IQLid: "147",
		AQLid: "169",
		EMCode: "247"
	},
	{
		QSid: "176",
		QDes: "/小纠结",
		IQLid: "146",
		AQLid: "168",
		EMCode: "246"
	},
	{
		QSid: "183",
		QDes: "/我最美",
		IQLid: "153",
		AQLid: "175",
		EMCode: "253"
	},
	{
		QSid: "262",
		QDes: "/脑阔疼",
		IQLid: "262",
		AQLid: "262",
		EMCode: "10262"
	},
	{
		QSid: "263",
		QDes: "/沧桑",
		IQLid: "263",
		AQLid: "263",
		EMCode: "10263"
	},
	{
		QSid: "264",
		QDes: "/捂脸",
		IQLid: "264",
		AQLid: "264",
		EMCode: "10264"
	},
	{
		QSid: "265",
		QDes: "/辣眼睛",
		IQLid: "265",
		AQLid: "265",
		EMCode: "10265"
	},
	{
		QSid: "266",
		QDes: "/哦哟",
		IQLid: "266",
		AQLid: "266",
		EMCode: "10266"
	},
	{
		QSid: "267",
		QDes: "/头秃",
		IQLid: "267",
		AQLid: "267",
		EMCode: "10267"
	},
	{
		QSid: "268",
		QDes: "/问号脸",
		IQLid: "268",
		AQLid: "268",
		EMCode: "10268"
	},
	{
		QSid: "269",
		QDes: "/暗中观察",
		IQLid: "269",
		AQLid: "269",
		EMCode: "10269"
	},
	{
		QSid: "270",
		QDes: "/emm",
		IQLid: "270",
		AQLid: "270",
		EMCode: "10270"
	},
	{
		QSid: "271",
		QDes: "/吃瓜",
		IQLid: "271",
		AQLid: "271",
		EMCode: "10271"
	},
	{
		QSid: "272",
		QDes: "/呵呵哒",
		IQLid: "272",
		AQLid: "272",
		EMCode: "10272"
	},
	{
		QSid: "277",
		QDes: "/汪汪",
		IQLid: "277",
		AQLid: "277",
		EMCode: "10277"
	},
	{
		QSid: "307",
		QDes: "/喵喵",
		IQLid: "307",
		AQLid: "307",
		EMCode: "10307"
	},
	{
		QSid: "306",
		QDes: "/牛气冲天",
		isStatic: "1",
		IQLid: "306",
		AQLid: "306",
		EMCode: "10306"
	},
	{
		QSid: "281",
		QDes: "/无眼笑",
		IQLid: "281",
		AQLid: "281",
		EMCode: "10281"
	},
	{
		QSid: "282",
		QDes: "/敬礼",
		IQLid: "282",
		AQLid: "282",
		EMCode: "10282"
	},
	{
		QSid: "283",
		QDes: "/狂笑",
		IQLid: "283",
		AQLid: "283",
		EMCode: "10283"
	},
	{
		QSid: "284",
		QDes: "/面无表情",
		IQLid: "284",
		AQLid: "284",
		EMCode: "10284"
	},
	{
		QSid: "285",
		QDes: "/摸鱼",
		IQLid: "285",
		AQLid: "285",
		EMCode: "10285"
	},
	{
		QSid: "293",
		QDes: "/摸锦鲤",
		IQLid: "293",
		AQLid: "293",
		EMCode: "10293"
	},
	{
		QSid: "286",
		QDes: "/魔鬼笑",
		IQLid: "286",
		AQLid: "286",
		EMCode: "10286"
	},
	{
		QSid: "287",
		QDes: "/哦",
		IQLid: "287",
		AQLid: "287",
		EMCode: "10287"
	},
	{
		QSid: "289",
		QDes: "/睁眼",
		IQLid: "289",
		AQLid: "289",
		EMCode: "10289"
	},
	{
		QSid: "294",
		QDes: "/期待",
		IQLid: "294",
		AQLid: "294",
		EMCode: "10294"
	},
	{
		QSid: "297",
		QDes: "/拜谢",
		IQLid: "297",
		AQLid: "297",
		EMCode: "10297"
	},
	{
		QSid: "298",
		QDes: "/元宝",
		IQLid: "298",
		AQLid: "298",
		EMCode: "10298"
	},
	{
		QSid: "299",
		QDes: "/牛啊",
		IQLid: "299",
		AQLid: "299",
		EMCode: "10299"
	},
	{
		QSid: "300",
		QDes: "/胖三斤",
		IQLid: "300",
		AQLid: "300",
		EMCode: "10300"
	},
	{
		QSid: "323",
		QDes: "/嫌弃",
		IQLid: "323",
		AQLid: "323",
		EMCode: "10323"
	},
	{
		QSid: "332",
		QDes: "/举牌牌",
		IQLid: "332",
		AQLid: "332",
		EMCode: "10332"
	},
	{
		QSid: "336",
		QDes: "/豹富",
		IQLid: "336",
		AQLid: "336",
		EMCode: "10336"
	},
	{
		QSid: "353",
		QDes: "/拜托",
		IQLid: "353",
		AQLid: "353",
		EMCode: "10353"
	},
	{
		QSid: "355",
		QDes: "/耶",
		IQLid: "355",
		AQLid: "355",
		EMCode: "10355"
	},
	{
		QSid: "356",
		QDes: "/666",
		IQLid: "356",
		AQLid: "356",
		EMCode: "10356"
	},
	{
		QSid: "354",
		QDes: "/尊嘟假嘟",
		IQLid: "354",
		AQLid: "354",
		EMCode: "10354"
	},
	{
		QSid: "352",
		QDes: "/咦",
		IQLid: "352",
		AQLid: "352",
		EMCode: "10352"
	},
	{
		QSid: "357",
		QDes: "/裂开",
		IQLid: "357",
		AQLid: "357",
		EMCode: "10357"
	},
	{
		QSid: "334",
		QDes: "/虎虎生威",
		IQLid: "334",
		AQLid: "334",
		EMCode: "10334"
	},
	{
		QSid: "347",
		QDes: "/大展宏兔",
		IQLid: "347",
		AQLid: "347",
		EMCode: "10347"
	},
	{
		QSid: "303",
		QDes: "/右拜年",
		IQLid: "303",
		AQLid: "303",
		EMCode: "10303"
	},
	{
		QSid: "302",
		QDes: "/左拜年",
		IQLid: "302",
		AQLid: "302",
		EMCode: "10302"
	},
	{
		QSid: "295",
		QDes: "/拿到红包",
		IQLid: "295",
		AQLid: "295",
		EMCode: "10295"
	},
	{
		QSid: "311",
		QDes: "/打call",
		IQLid: "311",
		AQLid: "311",
		EMCode: "10311",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "1"
	},
	{
		QSid: "312",
		QDes: "/变形",
		IQLid: "312",
		AQLid: "312",
		EMCode: "10312",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "2"
	},
	{
		QSid: "314",
		QDes: "/仔细分析",
		IQLid: "314",
		AQLid: "314",
		EMCode: "10314",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "4"
	},
	{
		QSid: "317",
		QDes: "/菜汪",
		IQLid: "317",
		AQLid: "317",
		EMCode: "10317",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "7"
	},
	{
		QSid: "318",
		QDes: "/崇拜",
		IQLid: "318",
		AQLid: "318",
		EMCode: "10318",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "8"
	},
	{
		QSid: "319",
		QDes: "/比心",
		IQLid: "319",
		AQLid: "319",
		EMCode: "10319",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "9"
	},
	{
		QSid: "320",
		QDes: "/庆祝",
		IQLid: "320",
		AQLid: "320",
		EMCode: "10320",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "10"
	},
	{
		QSid: "324",
		QDes: "/吃糖",
		IQLid: "324",
		AQLid: "324",
		EMCode: "10324",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "12"
	},
	{
		QSid: "325",
		QDes: "/惊吓",
		IQLid: "325",
		AQLid: "325",
		EMCode: "10325",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "14"
	},
	{
		QSid: "337",
		QDes: "/花朵脸",
		IQLid: "337",
		AQLid: "337",
		EMCode: "10337",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "22"
	},
	{
		QSid: "338",
		QDes: "/我想开了",
		IQLid: "338",
		AQLid: "338",
		EMCode: "10338",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "20"
	},
	{
		QSid: "339",
		QDes: "/舔屏",
		IQLid: "339",
		AQLid: "339",
		EMCode: "10339",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "21"
	},
	{
		QSid: "341",
		QDes: "/打招呼",
		IQLid: "341",
		AQLid: "341",
		EMCode: "10341",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "24"
	},
	{
		QSid: "342",
		QDes: "/酸Q",
		IQLid: "342",
		AQLid: "342",
		EMCode: "10342",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "26"
	},
	{
		QSid: "343",
		QDes: "/我方了",
		IQLid: "343",
		AQLid: "343",
		EMCode: "10343",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "27"
	},
	{
		QSid: "344",
		QDes: "/大怨种",
		IQLid: "344",
		AQLid: "344",
		EMCode: "10344",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "28"
	},
	{
		QSid: "345",
		QDes: "/红包多多",
		IQLid: "345",
		AQLid: "345",
		EMCode: "10345",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "29"
	},
	{
		QSid: "346",
		QDes: "/你真棒棒",
		IQLid: "346",
		AQLid: "346",
		EMCode: "10346",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "25"
	},
	{
		QSid: "181",
		QDes: "/戳一戳",
		IQLid: "151",
		AQLid: "173",
		EMCode: "251",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "37"
	},
	{
		QSid: "74",
		QDes: "/太阳",
		isStatic: "1",
		IQLid: "73",
		AQLid: "75",
		EMCode: "176",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "35"
	},
	{
		QSid: "75",
		QDes: "/月亮",
		isStatic: "1",
		IQLid: "67",
		AQLid: "68",
		EMCode: "175",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "36"
	},
	{
		QSid: "351",
		QDes: "/敲敲",
		IQLid: "351",
		AQLid: "351",
		EMCode: "10351",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "30"
	},
	{
		QSid: "349",
		QDes: "/坚强",
		IQLid: "349",
		AQLid: "349",
		EMCode: "10349",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "32"
	},
	{
		QSid: "350",
		QDes: "/贴贴",
		IQLid: "350",
		AQLid: "350",
		EMCode: "10350",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "31"
	},
	{
		QSid: "395",
		QDes: "/略略略",
		IQLid: "395",
		AQLid: "395",
		EMCode: "10395",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "41"
	},
	{
		QSid: "114",
		QDes: "/篮球",
		IQLid: "90",
		AQLid: "92",
		EMCode: "158",
		AniStickerType: 2,
		AniStickerPackId: "1",
		AniStickerId: "13"
	},
	{
		QSid: "358",
		QDes: "/骰子",
		IQLid: "358",
		AQLid: "358",
		QHide: "1",
		EMCode: "10358",
		AniStickerType: 2,
		AniStickerPackId: "1",
		AniStickerId: "33"
	},
	{
		QSid: "359",
		QDes: "/包剪锤",
		IQLid: "359",
		AQLid: "359",
		QHide: "1",
		EMCode: "10359",
		AniStickerType: 2,
		AniStickerPackId: "1",
		AniStickerId: "34"
	},
	{
		QSid: "326",
		QDes: "/生气",
		IQLid: "326",
		AQLid: "326",
		EMCode: "10326",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "15"
	},
	{
		QSid: "53",
		QDes: "/蛋糕",
		IQLid: "59",
		AQLid: "59",
		EMCode: "168",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "17"
	},
	{
		QSid: "49",
		QDes: "/拥抱",
		IQLid: "45",
		AQLid: "45",
		EMCode: "178"
	},
	{
		QSid: "66",
		QDes: "/爱心",
		IQLid: "28",
		AQLid: "28",
		EMCode: "166"
	},
	{
		QSid: "63",
		QDes: "/玫瑰",
		IQLid: "8",
		AQLid: "8",
		EMCode: "163"
	},
	{
		QSid: "64",
		QDes: "/凋谢",
		IQLid: "57",
		AQLid: "57",
		EMCode: "164"
	},
	{
		QSid: "187",
		QDes: "/幽灵",
		IQLid: "157",
		AQLid: "179",
		EMCode: "257"
	},
	{
		QSid: "146",
		QDes: "/爆筋",
		IQLid: "116",
		AQLid: "118",
		EMCode: "121011"
	},
	{
		QSid: "116",
		QDes: "/示爱",
		IQLid: "29",
		AQLid: "29",
		EMCode: "165"
	},
	{
		QSid: "67",
		QDes: "/心碎",
		IQLid: "72",
		AQLid: "74",
		EMCode: "167"
	},
	{
		QSid: "60",
		QDes: "/咖啡",
		IQLid: "66",
		AQLid: "66",
		EMCode: "160"
	},
	{
		QSid: "185",
		QDes: "/羊驼",
		IQLid: "155",
		AQLid: "177",
		EMCode: "255"
	},
	{
		QSid: "137",
		QDes: "/鞭炮",
		isStatic: "1",
		IQLid: "107",
		AQLid: "109",
		EMCode: "121002",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "18"
	},
	{
		QSid: "333",
		QDes: "/烟花",
		isStatic: "1",
		IQLid: "333",
		AQLid: "333",
		EMCode: "10333",
		AniStickerType: 1,
		AniStickerPackId: "1",
		AniStickerId: "19"
	},
	{
		QSid: "76",
		QDes: "/赞",
		IQLid: "52",
		AQLid: "52",
		EMCode: "179"
	},
	{
		QSid: "124",
		QDes: "/OK",
		IQLid: "64",
		AQLid: "64",
		EMCode: "189"
	},
	{
		QSid: "118",
		QDes: "/抱拳",
		IQLid: "56",
		AQLid: "56",
		EMCode: "183"
	},
	{
		QSid: "78",
		QDes: "/握手",
		IQLid: "54",
		AQLid: "54",
		EMCode: "181"
	},
	{
		QSid: "119",
		QDes: "/勾引",
		IQLid: "63",
		AQLid: "63",
		EMCode: "184"
	},
	{
		QSid: "79",
		QDes: "/胜利",
		IQLid: "55",
		AQLid: "55",
		EMCode: "182"
	},
	{
		QSid: "120",
		QDes: "/拳头",
		IQLid: "71",
		AQLid: "73",
		EMCode: "185"
	},
	{
		QSid: "121",
		QDes: "/差劲",
		IQLid: "70",
		AQLid: "72",
		EMCode: "186"
	},
	{
		QSid: "77",
		QDes: "/踩",
		IQLid: "53",
		AQLid: "53",
		EMCode: "180"
	},
	{
		QSid: "123",
		QDes: "/NO",
		IQLid: "92",
		AQLid: "94",
		EMCode: "188"
	},
	{
		QSid: "201",
		QDes: "/点赞",
		IQLid: "171",
		AQLid: "150",
		EMCode: "271"
	},
	{
		QSid: "273",
		QDes: "/我酸了",
		isStatic: "1",
		IQLid: "273",
		AQLid: "273",
		EMCode: "10273"
	},
	{
		QSid: "46",
		QDes: "/猪头",
		isStatic: "1",
		IQLid: "7",
		AQLid: "7",
		EMCode: "162"
	},
	{
		QSid: "112",
		QDes: "/菜刀",
		IQLid: "17",
		AQLid: "17",
		EMCode: "155"
	},
	{
		QSid: "56",
		QDes: "/刀",
		IQLid: "68",
		AQLid: "70",
		EMCode: "171"
	},
	{
		QSid: "169",
		QDes: "/手枪",
		isStatic: "1",
		IQLid: "139",
		AQLid: "141",
		EMCode: "121034"
	},
	{
		QSid: "171",
		QDes: "/茶",
		IQLid: "141",
		AQLid: "163",
		EMCode: "241"
	},
	{
		QSid: "59",
		QDes: "/便便",
		IQLid: "15",
		AQLid: "15",
		EMCode: "174"
	},
	{
		QSid: "144",
		QDes: "/喝彩",
		isStatic: "1",
		IQLid: "114",
		AQLid: "116",
		EMCode: "121009"
	},
	{
		QSid: "147",
		QDes: "/棒棒糖",
		isStatic: "1",
		IQLid: "117",
		AQLid: "119",
		EMCode: "121012"
	},
	{
		QSid: "89",
		QDes: "/西瓜",
		isStatic: "1",
		IQLid: "60",
		AQLid: "60",
		EMCode: "156"
	},
	{
		QSid: "148",
		QDes: "/喝奶",
		isStatic: "1",
		IQLid: "118",
		AQLid: "120",
		QHide: "1",
		EMCode: "121013"
	},
	{
		QSid: "55",
		QDes: "/炸弹",
		isStatic: "1",
		IQLid: "16",
		AQLid: "16",
		QHide: "1",
		EMCode: "170"
	},
	{
		QSid: "41",
		QDes: "/发抖",
		isStatic: "1",
		IQLid: "69",
		AQLid: "71",
		EMCode: "193"
	},
	{
		QSid: "125",
		QDes: "/转圈",
		IQLid: "95",
		AQLid: "97",
		EMCode: "195"
	},
	{
		QSid: "42",
		QDes: "/爱情",
		IQLid: "38",
		AQLid: "38",
		EMCode: "190"
	},
	{
		QSid: "43",
		QDes: "/跳跳",
		IQLid: "93",
		AQLid: "95",
		EMCode: "192"
	},
	{
		QSid: "86",
		QDes: "/怄火",
		IQLid: "94",
		AQLid: "96",
		EMCode: "194"
	},
	{
		QSid: "129",
		QDes: "/挥手",
		IQLid: "77",
		AQLid: "79",
		EMCode: "199"
	},
	{
		QSid: "226",
		QDes: "/拍桌",
		IQLid: "196",
		isCMEmoji: "1",
		AQLid: "198",
		QHide: "1",
		EMCode: "297"
	},
	{
		QSid: "85",
		QDes: "/飞吻",
		isStatic: "1",
		IQLid: "47",
		AQLid: "47",
		EMCode: "191"
	},
	{
		QSid: "215",
		QDes: "/糊脸",
		IQLid: "185",
		isCMEmoji: "1",
		AQLid: "187",
		QHide: "1",
		EMCode: "285"
	},
	{
		QSid: "214",
		QDes: "/啵啵",
		IQLid: "184",
		isCMEmoji: "1",
		AQLid: "186",
		QHide: "1",
		EMCode: "284"
	},
	{
		QSid: "222",
		QDes: "/抱抱",
		IQLid: "192",
		isCMEmoji: "1",
		AQLid: "194",
		QHide: "1",
		EMCode: "292"
	},
	{
		QSid: "203",
		QDes: "/托脸",
		IQLid: "173",
		AQLid: "152",
		QHide: "1",
		EMCode: "273"
	},
	{
		QSid: "235",
		QDes: "/颤抖",
		IQLid: "205",
		isCMEmoji: "1",
		AQLid: "207",
		QHide: "1",
		EMCode: "305"
	},
	{
		QSid: "241",
		QDes: "/生日快乐",
		IQLid: "211",
		isCMEmoji: "1",
		AQLid: "213",
		QHide: "1",
		EMCode: "311"
	},
	{
		QSid: "237",
		QDes: "/偷看",
		IQLid: "207",
		isCMEmoji: "1",
		AQLid: "209",
		QHide: "1",
		EMCode: "307"
	},
	{
		QSid: "218",
		QDes: "/舔一舔",
		IQLid: "188",
		isCMEmoji: "1",
		AQLid: "190",
		QHide: "1",
		EMCode: "288"
	},
	{
		QSid: "233",
		QDes: "/掐一掐",
		IQLid: "203",
		isCMEmoji: "1",
		AQLid: "205",
		QHide: "1",
		EMCode: "303"
	},
	{
		QSid: "232",
		QDes: "/佛系",
		IQLid: "202",
		isCMEmoji: "1",
		AQLid: "204",
		QHide: "1",
		EMCode: "302"
	},
	{
		QSid: "238",
		QDes: "/扇脸",
		IQLid: "208",
		isCMEmoji: "1",
		AQLid: "210",
		QHide: "1",
		EMCode: "308"
	},
	{
		QSid: "217",
		QDes: "/扯一扯",
		IQLid: "187",
		isCMEmoji: "1",
		AQLid: "189",
		QHide: "1",
		EMCode: "287"
	},
	{
		QSid: "225",
		QDes: "/撩一撩",
		IQLid: "195",
		isCMEmoji: "1",
		AQLid: "197",
		QHide: "1",
		EMCode: "296"
	},
	{
		QSid: "230",
		QDes: "/嘲讽",
		IQLid: "200",
		isCMEmoji: "1",
		AQLid: "202",
		QHide: "1",
		EMCode: "300"
	},
	{
		QSid: "194",
		QDes: "/不开心",
		IQLid: "164",
		AQLid: "143",
		QHide: "1",
		EMCode: "264"
	},
	{
		QSid: "210",
		QDes: "/飙泪",
		IQLid: "180",
		AQLid: "159",
		QHide: "1",
		EMCode: "280"
	},
	{
		QSid: "193",
		QDes: "/大笑",
		IQLid: "163",
		AQLid: "185",
		QHide: "1",
		EMCode: "263"
	},
	{
		QSid: "204",
		QDes: "/吃",
		IQLid: "174",
		AQLid: "153",
		QHide: "1",
		EMCode: "274"
	},
	{
		QSid: "200",
		QDes: "/求求",
		IQLid: "170",
		AQLid: "149",
		QHide: "1",
		EMCode: "270"
	},
	{
		QSid: "290",
		QDes: "/敲开心",
		IQLid: "290",
		isCMEmoji: "1",
		AQLid: "290",
		QHide: "1",
		EMCode: "20240"
	},
	{
		QSid: "224",
		QDes: "/开枪",
		IQLid: "194",
		isCMEmoji: "1",
		AQLid: "196",
		QHide: "1",
		EMCode: "295"
	},
	{
		QSid: "229",
		QDes: "/干杯",
		IQLid: "199",
		isCMEmoji: "1",
		AQLid: "201",
		QHide: "1",
		EMCode: "299"
	},
	{
		QSid: "221",
		QDes: "/顶呱呱",
		IQLid: "191",
		isCMEmoji: "1",
		AQLid: "193",
		QHide: "1",
		EMCode: "291"
	},
	{
		QSid: "219",
		QDes: "/蹭一蹭",
		IQLid: "189",
		isCMEmoji: "1",
		AQLid: "191",
		QHide: "1",
		EMCode: "289"
	},
	{
		QSid: "227",
		QDes: "/拍手",
		IQLid: "197",
		isCMEmoji: "1",
		AQLid: "199",
		QHide: "1",
		EMCode: "294"
	},
	{
		QSid: "216",
		QDes: "/拍头",
		IQLid: "186",
		isCMEmoji: "1",
		AQLid: "188",
		QHide: "1",
		EMCode: "286"
	},
	{
		QSid: "231",
		QDes: "/哼",
		IQLid: "201",
		isCMEmoji: "1",
		AQLid: "203",
		QHide: "1",
		EMCode: "301"
	},
	{
		QSid: "244",
		QDes: "/扔狗",
		IQLid: "214",
		isCMEmoji: "1",
		AQLid: "216",
		QHide: "1",
		EMCode: "312"
	},
	{
		QSid: "223",
		QDes: "/暴击",
		IQLid: "193",
		isCMEmoji: "1",
		AQLid: "195",
		QHide: "1",
		EMCode: "293"
	},
	{
		QSid: "243",
		QDes: "/甩头",
		IQLid: "213",
		isCMEmoji: "1",
		AQLid: "215",
		QHide: "1",
		EMCode: "313"
	},
	{
		QSid: "211",
		QDes: "/我不看",
		IQLid: "181",
		AQLid: "160",
		QHide: "1",
		EMCode: "281"
	},
	{
		QSid: "292",
		QDes: "/让我康康",
		IQLid: "292",
		isCMEmoji: "1",
		AQLid: "292",
		QHide: "1",
		EMCode: "20242"
	},
	{
		QSid: "240",
		QDes: "/喷脸",
		IQLid: "210",
		isCMEmoji: "1",
		AQLid: "212",
		QHide: "1",
		EMCode: "310"
	},
	{
		QSid: "180",
		QDes: "/惊喜",
		IQLid: "150",
		AQLid: "172",
		QHide: "1",
		EMCode: "250"
	},
	{
		QSid: "122",
		QDes: "/爱你",
		IQLid: "65",
		AQLid: "65",
		QHide: "1",
		EMCode: "187"
	},
	{
		QSid: "202",
		QDes: "/无聊",
		IQLid: "172",
		AQLid: "151",
		QHide: "1",
		EMCode: "272"
	},
	{
		QSid: "278",
		QDes: "/汗",
		IQLid: "278",
		isCMEmoji: "1",
		AQLid: "278",
		QHide: "1",
		EMCode: "20237"
	},
	{
		QSid: "301",
		QDes: "/好闪",
		IQLid: "301",
		AQLid: "301",
		QHide: "1",
		EMCode: "10301"
	},
	{
		QSid: "288",
		QDes: "/请",
		IQLid: "288",
		AQLid: "288",
		QHide: "1",
		EMCode: "10288"
	},
	{
		QSid: "322",
		QDes: "/拒绝",
		IQLid: "322",
		AQLid: "322",
		QHide: "1",
		EMCode: "10322"
	},
	{
		QSid: "198",
		QDes: "/呃",
		IQLid: "168",
		AQLid: "147",
		QHide: "1",
		EMCode: "268"
	},
	{
		QSid: "348",
		QDes: "/福萝卜",
		IQLid: "348",
		AQLid: "348",
		QHide: "1",
		EMCode: "10348"
	},
	{
		QSid: "206",
		QDes: "/害怕",
		IQLid: "176",
		AQLid: "155",
		QHide: "1",
		EMCode: "276"
	},
	{
		QSid: "239",
		QDes: "/原谅",
		IQLid: "209",
		isCMEmoji: "1",
		AQLid: "211",
		QHide: "1",
		EMCode: "309"
	}
];
const emoji = [
	{
		QSid: "😊",
		QCid: "128522",
		AQLid: "0",
		QDes: "/嘿嘿",
		EMCode: "400832"
	},
	{
		QSid: "😌",
		QCid: "128524",
		AQLid: "1",
		QDes: "/羞涩",
		EMCode: "400834"
	},
	{
		QSid: "😚",
		QCid: "128538",
		AQLid: "2",
		QDes: "/亲亲",
		EMCode: "400848"
	},
	{
		QSid: "😓",
		QCid: "128531",
		AQLid: "3",
		QDes: "/汗",
		EMCode: "400841"
	},
	{
		QSid: "😰",
		QCid: "128560",
		AQLid: "4",
		QDes: "/紧张",
		EMCode: "400870"
	},
	{
		QSid: "😝",
		QCid: "128541",
		AQLid: "5",
		QDes: "/吐舌",
		EMCode: "400851"
	},
	{
		QSid: "😁",
		QCid: "128513",
		AQLid: "6",
		QDes: "/呲牙",
		EMCode: "400823"
	},
	{
		QSid: "😜",
		QCid: "128540",
		AQLid: "7",
		QDes: "/淘气",
		EMCode: "400850"
	},
	{
		QSid: "☺",
		QCid: "9786",
		AQLid: "8",
		QDes: "/可爱",
		EMCode: "401181"
	},
	{
		QSid: "😉",
		QCid: "128521",
		AQLid: "9",
		QDes: "/媚眼",
		QHide: "1",
		EMCode: "400831"
	},
	{
		QSid: "😍",
		QCid: "128525",
		AQLid: "10",
		QDes: "/花痴",
		EMCode: "400835"
	},
	{
		QSid: "😔",
		QCid: "128532",
		AQLid: "11",
		QDes: "/失落",
		EMCode: "400842"
	},
	{
		QSid: "😄",
		QCid: "128516",
		AQLid: "12",
		QDes: "/高兴",
		EMCode: "400826"
	},
	{
		QSid: "😏",
		QCid: "128527",
		AQLid: "13",
		QDes: "/哼哼",
		EMCode: "400837"
	},
	{
		QSid: "😒",
		QCid: "128530",
		AQLid: "14",
		QDes: "/不屑",
		EMCode: "400840"
	},
	{
		QSid: "😳",
		QCid: "128563",
		AQLid: "15",
		QDes: "/瞪眼",
		EMCode: "400873"
	},
	{
		QSid: "😘",
		QCid: "128536",
		AQLid: "16",
		QDes: "/飞吻",
		EMCode: "400846"
	},
	{
		QSid: "😭",
		QCid: "128557",
		AQLid: "17",
		QDes: "/大哭",
		EMCode: "400867"
	},
	{
		QSid: "😱",
		QCid: "128561",
		AQLid: "18",
		QDes: "/害怕",
		EMCode: "400871"
	},
	{
		QSid: "😂",
		QCid: "128514",
		AQLid: "19",
		QDes: "/激动",
		EMCode: "400824"
	},
	{
		QSid: "💪",
		QCid: "128170",
		AQLid: "20",
		QDes: "/肌肉",
		EMCode: "400644"
	},
	{
		QSid: "👊",
		QCid: "128074",
		AQLid: "21",
		QDes: "/拳头",
		EMCode: "400390"
	},
	{
		QSid: "👍",
		QCid: "128077",
		AQLid: "22",
		QDes: "/厉害",
		EMCode: "400408"
	},
	{
		QSid: "☝",
		QCid: "9757",
		AQLid: "23",
		QDes: "/向上",
		QHide: "1",
		EMCode: "401203"
	},
	{
		QSid: "👏",
		QCid: "128079",
		AQLid: "24",
		QDes: "/鼓掌",
		EMCode: "400420"
	},
	{
		QSid: "✌",
		QCid: "9996",
		AQLid: "25",
		QDes: "/胜利",
		QHide: "1",
		EMCode: "401210"
	},
	{
		QSid: "👎",
		QCid: "128078",
		AQLid: "26",
		QDes: "/鄙视",
		EMCode: "400414"
	},
	{
		QSid: "🙏",
		QCid: "128591",
		AQLid: "27",
		QDes: "/合十",
		EMCode: "400396"
	},
	{
		QSid: "👌",
		QCid: "128076",
		AQLid: "28",
		QDes: "/好的",
		EMCode: "400402"
	},
	{
		QSid: "👈",
		QCid: "128072",
		AQLid: "29",
		QDes: "/向左",
		QHide: "1",
		EMCode: "400378"
	},
	{
		QSid: "👉",
		QCid: "128073",
		AQLid: "30",
		QDes: "/向右",
		QHide: "1",
		EMCode: "400384"
	},
	{
		QSid: "👆",
		QCid: "128070",
		AQLid: "31",
		QDes: "/向上",
		EMCode: "400366"
	},
	{
		QSid: "👇",
		QCid: "128071",
		AQLid: "32",
		QDes: "/向下",
		QHide: "1",
		EMCode: "400372"
	},
	{
		QSid: "👀",
		QCid: "128064",
		AQLid: "33",
		QDes: "/眼睛",
		EMCode: "400351"
	},
	{
		QSid: "👃",
		QCid: "128067",
		AQLid: "34",
		QDes: "/鼻子",
		QHide: "1",
		EMCode: "400358"
	},
	{
		QSid: "👄",
		QCid: "128068",
		AQLid: "35",
		QDes: "/嘴唇",
		QHide: "1",
		EMCode: "400364"
	},
	{
		QSid: "👂",
		QCid: "128066",
		AQLid: "36",
		QDes: "/耳朵",
		QHide: "1",
		EMCode: "400352"
	},
	{
		QSid: "🍚",
		QCid: "127834",
		AQLid: "37",
		QDes: "/米饭",
		QHide: "1",
		EMCode: "400149"
	},
	{
		QSid: "🍝",
		QCid: "127837",
		AQLid: "38",
		QDes: "/意面",
		QHide: "1",
		EMCode: "400152"
	},
	{
		QSid: "🍜",
		QCid: "127836",
		AQLid: "39",
		QDes: "/拉面",
		EMCode: "400151"
	},
	{
		QSid: "🍙",
		QCid: "127833",
		AQLid: "40",
		QDes: "/饭团",
		QHide: "1",
		EMCode: "400148"
	},
	{
		QSid: "🍧",
		QCid: "127847",
		AQLid: "41",
		QDes: "/刨冰",
		EMCode: "400162"
	},
	{
		QSid: "🍣",
		QCid: "127843",
		AQLid: "42",
		QDes: "/寿司",
		QHide: "1",
		EMCode: "400158"
	},
	{
		QSid: "🎂",
		QCid: "127874",
		AQLid: "43",
		QDes: "/蛋糕",
		QHide: "1",
		EMCode: "400186"
	},
	{
		QSid: "🍞",
		QCid: "127838",
		AQLid: "44",
		QDes: "/面包",
		EMCode: "400153"
	},
	{
		QSid: "🍔",
		QCid: "127828",
		AQLid: "45",
		QDes: "/汉堡",
		QHide: "1",
		EMCode: "400143"
	},
	{
		QSid: "🍳",
		QCid: "127859",
		AQLid: "46",
		QDes: "/煎蛋",
		QHide: "1",
		EMCode: "400174"
	},
	{
		QSid: "🍟",
		QCid: "127839",
		AQLid: "47",
		QDes: "/薯条",
		QHide: "1",
		EMCode: "400154"
	},
	{
		QSid: "🍺",
		QCid: "127866",
		AQLid: "48",
		QDes: "/啤酒",
		EMCode: "400181"
	},
	{
		QSid: "🍻",
		QCid: "127867",
		AQLid: "49",
		QDes: "/干杯",
		EMCode: "400182"
	},
	{
		QSid: "🍸",
		QCid: "127864",
		AQLid: "50",
		QDes: "/高脚杯",
		QHide: "1",
		EMCode: "400179"
	},
	{
		QSid: "☕",
		QCid: "9749",
		AQLid: "51",
		QDes: "/咖啡",
		EMCode: "401262"
	},
	{
		QSid: "🍎",
		QCid: "127822",
		AQLid: "52",
		QDes: "/苹果",
		EMCode: "400137"
	},
	{
		QSid: "🍊",
		QCid: "127818",
		AQLid: "53",
		QDes: "/橙子",
		QHide: "1",
		EMCode: "400133"
	},
	{
		QSid: "🍓",
		QCid: "127827",
		AQLid: "54",
		QDes: "/草莓",
		EMCode: "400142"
	},
	{
		QSid: "🍉",
		QCid: "127817",
		AQLid: "55",
		QDes: "/西瓜",
		EMCode: "400132"
	},
	{
		QSid: "💊",
		QCid: "128138",
		AQLid: "56",
		QDes: "/药丸",
		QHide: "1",
		EMCode: "400612"
	},
	{
		QSid: "🚬",
		QCid: "128684",
		AQLid: "57",
		QDes: "/吸烟",
		EMCode: "400987"
	},
	{
		QSid: "🎄",
		QCid: "127876",
		AQLid: "58",
		QDes: "/圣诞树",
		QHide: "1",
		EMCode: "400188"
	},
	{
		QSid: "🌹",
		QCid: "127801",
		AQLid: "59",
		QDes: "/玫瑰",
		EMCode: "400116"
	},
	{
		QSid: "🎉",
		QCid: "127881",
		AQLid: "60",
		QDes: "/庆祝",
		EMCode: "400198"
	},
	{
		QSid: "🌴",
		QCid: "127796",
		AQLid: "61",
		QDes: "/椰子树",
		QHide: "1",
		EMCode: "400112"
	},
	{
		QSid: "💝",
		QCid: "128157",
		AQLid: "62",
		QDes: "/礼物",
		EMCode: "400631"
	},
	{
		QSid: "🎀",
		QCid: "127872",
		AQLid: "63",
		QDes: "/蝴蝶结",
		QHide: "1",
		EMCode: "400184"
	},
	{
		QSid: "🎈",
		QCid: "127880",
		AQLid: "64",
		QDes: "/气球",
		QHide: "1",
		EMCode: "400197"
	},
	{
		QSid: "🐚",
		QCid: "128026",
		AQLid: "65",
		QDes: "/海螺",
		QHide: "1",
		EMCode: "400314"
	},
	{
		QSid: "💍",
		QCid: "128141",
		AQLid: "66",
		QDes: "/戒指",
		QHide: "1",
		EMCode: "400615"
	},
	{
		QSid: "💣",
		QCid: "128163",
		AQLid: "67",
		QDes: "/炸弹",
		EMCode: "400637"
	},
	{
		QSid: "👑",
		QCid: "128081",
		AQLid: "68",
		QDes: "/皇冠",
		QHide: "1",
		EMCode: "400432"
	},
	{
		QSid: "🔔",
		QCid: "128276",
		AQLid: "69",
		QDes: "/铃铛",
		QHide: "1",
		EMCode: "400751"
	},
	{
		QSid: "⭐",
		QCid: "11088",
		AQLid: "70",
		QDes: "/星星",
		QHide: "1",
		EMCode: "401686"
	},
	{
		QSid: "✨",
		QCid: "10024",
		AQLid: "71",
		QDes: "/闪光",
		EMCode: "401137"
	},
	{
		QSid: "💨",
		QCid: "128168",
		AQLid: "72",
		QDes: "/吹气",
		EMCode: "400642"
	},
	{
		QSid: "💦",
		QCid: "128166",
		AQLid: "73",
		QDes: "/水",
		EMCode: "400640"
	},
	{
		QSid: "🔥",
		QCid: "128293",
		AQLid: "74",
		QDes: "/火",
		EMCode: "400768"
	},
	{
		QSid: "🏆",
		QCid: "127942",
		AQLid: "75",
		QDes: "/奖杯",
		QHide: "1",
		EMCode: "400256"
	},
	{
		QSid: "💰",
		QCid: "128176",
		AQLid: "76",
		QDes: "/钱",
		QHide: "1",
		EMCode: "400655"
	},
	{
		QSid: "💤",
		QCid: "128164",
		AQLid: "77",
		QDes: "/睡觉",
		EMCode: "400638"
	},
	{
		QSid: "⚡",
		QCid: "9889",
		AQLid: "78",
		QDes: "/闪电",
		QHide: "1",
		EMCode: "401685"
	},
	{
		QSid: "👣",
		QCid: "128099",
		AQLid: "79",
		QDes: "/脚印",
		QHide: "1",
		EMCode: "400450"
	},
	{
		QSid: "💩",
		QCid: "128169",
		AQLid: "80",
		QDes: "/便便",
		EMCode: "400643"
	},
	{
		QSid: "💉",
		QCid: "128137",
		AQLid: "81",
		QDes: "/打针",
		EMCode: "400611"
	},
	{
		QSid: "♨",
		QCid: "9832",
		AQLid: "82",
		QDes: "/热",
		QHide: "1",
		EMCode: "401287"
	},
	{
		QSid: "📫",
		QCid: "128235",
		AQLid: "83",
		QDes: "/邮箱",
		EMCode: "400714"
	},
	{
		QSid: "🔑",
		QCid: "128273",
		AQLid: "84",
		QDes: "/钥匙",
		QHide: "1",
		EMCode: "400748"
	},
	{
		QSid: "🔒",
		QCid: "128274",
		AQLid: "85",
		QDes: "/锁",
		QHide: "1",
		EMCode: "400749"
	},
	{
		QSid: "✈",
		QCid: "9992",
		AQLid: "86",
		QDes: "/飞机",
		QHide: "1",
		EMCode: "401298"
	},
	{
		QSid: "🚄",
		QCid: "128644",
		AQLid: "87",
		QDes: "/列车",
		QHide: "1",
		EMCode: "400942"
	},
	{
		QSid: "🚗",
		QCid: "128663",
		AQLid: "88",
		QDes: "/汽车",
		QHide: "1",
		EMCode: "400961"
	},
	{
		QSid: "🚤",
		QCid: "128676",
		AQLid: "89",
		QDes: "/快艇",
		QHide: "1",
		EMCode: "400979"
	},
	{
		QSid: "🚲",
		QCid: "128690",
		AQLid: "90",
		QDes: "/自行车",
		QHide: "1",
		EMCode: "400993"
	},
	{
		QSid: "🐎",
		QCid: "128014",
		AQLid: "91",
		QDes: "/骑马",
		EMCode: "400302"
	},
	{
		QSid: "🚀",
		QCid: "128640",
		AQLid: "92",
		QDes: "/火箭",
		QHide: "1",
		EMCode: "400938"
	},
	{
		QSid: "🚌",
		QCid: "128652",
		AQLid: "93",
		QDes: "/公交",
		QHide: "1",
		EMCode: "400950"
	},
	{
		QSid: "⛵",
		QCid: "9973",
		AQLid: "94",
		QDes: "/船",
		QHide: "1",
		EMCode: "401294"
	},
	{
		QSid: "👩",
		QCid: "128105",
		AQLid: "95",
		QDes: "/妈妈",
		QHide: "1",
		EMCode: "400482"
	},
	{
		QSid: "👨",
		QCid: "128104",
		AQLid: "96",
		QDes: "/爸爸",
		QHide: "1",
		EMCode: "400465"
	},
	{
		QSid: "👧",
		QCid: "128103",
		AQLid: "97",
		QDes: "/女孩",
		EMCode: "400459"
	},
	{
		QSid: "👦",
		QCid: "128102",
		AQLid: "98",
		QDes: "/男孩",
		EMCode: "400453"
	},
	{
		QSid: "🐵",
		QCid: "128053",
		AQLid: "99",
		QDes: "/猴",
		EMCode: "400341"
	},
	{
		QSid: "🐙",
		QCid: "128025",
		AQLid: "100",
		QDes: "/章鱼",
		QHide: "1",
		EMCode: "400313"
	},
	{
		QSid: "🐷",
		QCid: "128055",
		AQLid: "101",
		QDes: "/猪",
		EMCode: "400343"
	},
	{
		QSid: "💀",
		QCid: "128128",
		AQLid: "102",
		QDes: "/骷髅",
		QHide: "1",
		EMCode: "400572"
	},
	{
		QSid: "🐤",
		QCid: "128036",
		AQLid: "103",
		QDes: "/小鸡",
		QHide: "1",
		EMCode: "400324"
	},
	{
		QSid: "🐨",
		QCid: "128040",
		AQLid: "104",
		QDes: "/树懒",
		QHide: "1",
		EMCode: "400328"
	},
	{
		QSid: "🐮",
		QCid: "128046",
		AQLid: "105",
		QDes: "/牛",
		EMCode: "400334"
	},
	{
		QSid: "🐔",
		QCid: "128020",
		AQLid: "106",
		QDes: "/公鸡",
		EMCode: "400308"
	},
	{
		QSid: "🐸",
		QCid: "128056",
		AQLid: "107",
		QDes: "/青蛙",
		EMCode: "400344"
	},
	{
		QSid: "👻",
		QCid: "128123",
		AQLid: "108",
		QDes: "/幽灵",
		EMCode: "400562"
	},
	{
		QSid: "🐛",
		QCid: "128027",
		AQLid: "109",
		QDes: "/虫",
		EMCode: "400315"
	},
	{
		QSid: "🐠",
		QCid: "128032",
		AQLid: "110",
		QDes: "/鱼",
		QHide: "1",
		EMCode: "400320"
	},
	{
		QSid: "🐶",
		QCid: "128054",
		AQLid: "111",
		QDes: "/狗",
		EMCode: "400342"
	},
	{
		QSid: "🐯",
		QCid: "128047",
		AQLid: "112",
		QDes: "/老虎",
		QHide: "1",
		EMCode: "400335"
	},
	{
		QSid: "👼",
		QCid: "128124",
		AQLid: "113",
		QDes: "/天使",
		QHide: "1",
		EMCode: "400563"
	},
	{
		QSid: "🐧",
		QCid: "128039",
		AQLid: "114",
		QDes: "/企鹅",
		QHide: "1",
		EMCode: "400327"
	},
	{
		QSid: "🐳",
		QCid: "128051",
		AQLid: "115",
		QDes: "/鲸鱼",
		EMCode: "400339"
	},
	{
		QSid: "🐭",
		QCid: "128045",
		AQLid: "116",
		QDes: "/老鼠",
		QHide: "1",
		EMCode: "400333"
	},
	{
		QSid: "👒",
		QCid: "128082",
		AQLid: "117",
		QDes: "/帽子",
		QHide: "1",
		EMCode: "400433"
	},
	{
		QSid: "👗",
		QCid: "128087",
		AQLid: "118",
		QDes: "/连衣裙",
		QHide: "1",
		EMCode: "400438"
	},
	{
		QSid: "💄",
		QCid: "128132",
		AQLid: "119",
		QDes: "/口红",
		QHide: "1",
		EMCode: "400591"
	},
	{
		QSid: "👠",
		QCid: "128096",
		AQLid: "120",
		QDes: "/高跟鞋",
		QHide: "1",
		EMCode: "400447"
	},
	{
		QSid: "👢",
		QCid: "128098",
		AQLid: "121",
		QDes: "/靴子",
		EMCode: "400449"
	},
	{
		QSid: "🌂",
		QCid: "127746",
		AQLid: "122",
		QDes: "/雨伞",
		QHide: "1",
		EMCode: "400077"
	},
	{
		QSid: "👜",
		QCid: "128092",
		AQLid: "123",
		QDes: "/包",
		QHide: "1",
		EMCode: "400443"
	},
	{
		QSid: "👙",
		QCid: "128089",
		AQLid: "124",
		QDes: "/内衣",
		QHide: "1",
		EMCode: "400440"
	},
	{
		QSid: "👕",
		QCid: "128085",
		AQLid: "125",
		QDes: "/衣服",
		QHide: "1",
		EMCode: "400436"
	},
	{
		QSid: "👟",
		QCid: "128095",
		AQLid: "126",
		QDes: "/鞋子",
		QHide: "1",
		EMCode: "400446"
	},
	{
		QSid: "☁",
		QCid: "9729",
		AQLid: "127",
		QDes: "/云朵",
		QHide: "1",
		EMCode: "401329"
	},
	{
		QSid: "☀",
		QCid: "9728",
		AQLid: "128",
		QDes: "/晴天",
		EMCode: "401328"
	},
	{
		QSid: "☔",
		QCid: "9748",
		AQLid: "129",
		QDes: "/雨天",
		QHide: "1",
		EMCode: "401342"
	},
	{
		QSid: "🌙",
		QCid: "127769",
		AQLid: "130",
		QDes: "/月亮",
		QHide: "1",
		EMCode: "400100"
	},
	{
		QSid: "⛄",
		QCid: "9924",
		AQLid: "131",
		QDes: "/雪人",
		QHide: "1",
		EMCode: "401346"
	},
	{
		QSid: "⭕",
		QCid: "11093",
		AQLid: "132",
		QDes: "/正确",
		QHide: "1",
		EMCode: "401687"
	},
	{
		QSid: "❌",
		QCid: "10060",
		AQLid: "133",
		QDes: "/错误",
		QHide: "1",
		EMCode: "401142"
	},
	{
		QSid: "❔",
		QCid: "10068",
		AQLid: "134",
		QDes: "/问号",
		EMCode: "401145"
	},
	{
		QSid: "❕",
		QCid: "10069",
		AQLid: "135",
		QDes: "/叹号",
		QHide: "1",
		EMCode: "401146"
	},
	{
		QSid: "☎",
		QCid: "9742",
		AQLid: "136",
		QDes: "/电话",
		QHide: "1",
		EMCode: "401398"
	},
	{
		QSid: "📷",
		QCid: "128247",
		AQLid: "137",
		QDes: "/相机",
		QHide: "1",
		EMCode: "400726"
	},
	{
		QSid: "📱",
		QCid: "128241",
		AQLid: "138",
		QDes: "/手机",
		QHide: "1",
		EMCode: "400720"
	},
	{
		QSid: "📠",
		QCid: "128224",
		AQLid: "139",
		QDes: "/传真",
		QHide: "1",
		EMCode: "400703"
	},
	{
		QSid: "💻",
		QCid: "128187",
		AQLid: "140",
		QDes: "/电脑",
		QHide: "1",
		EMCode: "400666"
	},
	{
		QSid: "🎥",
		QCid: "127909",
		AQLid: "141",
		QDes: "/摄影机",
		QHide: "1",
		EMCode: "400214"
	},
	{
		QSid: "🎤",
		QCid: "127908",
		AQLid: "142",
		QDes: "/话筒",
		QHide: "1",
		EMCode: "400213"
	},
	{
		QSid: "🔫",
		QCid: "128299",
		AQLid: "143",
		QDes: "/手枪",
		EMCode: "400774"
	},
	{
		QSid: "💿",
		QCid: "128191",
		AQLid: "144",
		QDes: "/光碟",
		QHide: "1",
		EMCode: "400670"
	},
	{
		QSid: "💓",
		QCid: "128147",
		AQLid: "145",
		QDes: "/爱心",
		EMCode: "400621"
	},
	{
		QSid: "♣",
		QCid: "9827",
		AQLid: "146",
		QDes: "/扑克",
		QHide: "1",
		EMCode: "401385"
	},
	{
		QSid: "🀄",
		QCid: "126980",
		AQLid: "147",
		QDes: "/麻将",
		QHide: "1",
		EMCode: "401386"
	},
	{
		QSid: "〽",
		QCid: "12349",
		AQLid: "148",
		QDes: "/股票",
		QHide: "1",
		EMCode: "401691"
	},
	{
		QSid: "🎰",
		QCid: "127920",
		AQLid: "149",
		QDes: "/老虎机",
		QHide: "1",
		EMCode: "400225"
	},
	{
		QSid: "🚥",
		QCid: "128677",
		AQLid: "150",
		QDes: "/信号灯",
		QHide: "1",
		EMCode: "400980"
	},
	{
		QSid: "🚧",
		QCid: "128679",
		AQLid: "151",
		QDes: "/路障",
		QHide: "1",
		EMCode: "400982"
	},
	{
		QSid: "🎸",
		QCid: "127928",
		AQLid: "152",
		QDes: "/吉他",
		QHide: "1",
		EMCode: "400233"
	},
	{
		QSid: "💈",
		QCid: "128136",
		AQLid: "153",
		QDes: "/理发厅",
		QHide: "1",
		EMCode: "400610"
	},
	{
		QSid: "🛀",
		QCid: "128704",
		AQLid: "154",
		QDes: "/浴缸",
		QHide: "1",
		EMCode: "401022"
	},
	{
		QSid: "🚽",
		QCid: "128701",
		AQLid: "155",
		QDes: "/马桶",
		QHide: "1",
		EMCode: "401019"
	},
	{
		QSid: "🏠",
		QCid: "127968",
		AQLid: "156",
		QDes: "/家",
		QHide: "1",
		EMCode: "400271"
	},
	{
		QSid: "⛪",
		QCid: "9962",
		AQLid: "157",
		QDes: "/教堂",
		QHide: "1",
		EMCode: "401281"
	},
	{
		QSid: "🏦",
		QCid: "127974",
		AQLid: "158",
		QDes: "/银行",
		QHide: "1",
		EMCode: "400277"
	},
	{
		QSid: "🏥",
		QCid: "127973",
		AQLid: "159",
		QDes: "/医院",
		QHide: "1",
		EMCode: "400276"
	},
	{
		QSid: "🏨",
		QCid: "127976",
		AQLid: "160",
		QDes: "/酒店",
		QHide: "1",
		EMCode: "400279"
	},
	{
		QSid: "🏧",
		QCid: "127975",
		AQLid: "161",
		QDes: "/取款机",
		QHide: "1",
		EMCode: "400278"
	},
	{
		QSid: "🏪",
		QCid: "127978",
		AQLid: "162",
		QDes: "/便利店",
		EMCode: "400281"
	},
	{
		QSid: "🚹",
		QCid: "128697",
		AQLid: "163",
		QDes: "/男性",
		QHide: "1",
		EMCode: "401015"
	},
	{
		QSid: "🚺",
		QCid: "128698",
		AQLid: "164",
		QDes: "/女性",
		QHide: "1",
		EMCode: "401016"
	}
];
const faceConfig = {
	sysface: sysface,
	emoji: emoji
};

const mFaceCache = /* @__PURE__ */ new Map();
class SendMsgElementConstructor {
  static location() {
    return {
      elementType: ElementType.SHARELOCATION,
      elementId: "",
      shareLocationElement: {
        text: "测试",
        ext: ""
      }
    };
  }
  static text(content) {
    return {
      elementType: ElementType.TEXT,
      elementId: "",
      textElement: {
        content,
        atType: AtType.notAt,
        atUid: "",
        atTinyId: "",
        atNtUid: ""
      }
    };
  }
  static at(atUid, atNtUid, atType, atName) {
    return {
      elementType: ElementType.TEXT,
      elementId: "",
      textElement: {
        content: `@${atName}`,
        atType,
        atUid,
        atTinyId: "",
        atNtUid
      }
    };
  }
  static reply(msgSeq, msgId, senderUin, senderUinStr) {
    return {
      elementType: ElementType.REPLY,
      elementId: "",
      replyElement: {
        replayMsgSeq: msgSeq,
        // raw.msgSeq
        replayMsgId: msgId,
        // raw.msgId
        senderUin,
        senderUinStr
      }
    };
  }
  static async pic(picPath, summary = "", subType = 0) {
    const {
      md5,
      fileName,
      path,
      fileSize
    } = await NTQQFileApi.uploadFile(picPath, ElementType.PIC, subType);
    if (fileSize === 0) {
      throw "文件异常，大小为0";
    }
    const imageSize = await NTQQFileApi.getImageSize(picPath);
    const picElement = {
      md5HexStr: md5,
      fileSize: fileSize.toString(),
      picWidth: imageSize?.width,
      picHeight: imageSize?.height,
      fileName,
      sourcePath: path,
      original: true,
      picType: isGIF(picPath) ? PicType.gif : PicType.jpg,
      picSubType: subType,
      fileUuid: "",
      fileSubId: "",
      thumbFileSize: 0,
      summary
    };
    return {
      elementType: ElementType.PIC,
      elementId: "",
      picElement
    };
  }
  static async file(filePath, fileName = "", folderId = "") {
    const {
      md5,
      fileName: _fileName,
      path,
      fileSize
    } = await NTQQFileApi.uploadFile(filePath, ElementType.FILE);
    if (fileSize === 0) {
      throw "文件异常，大小为0";
    }
    const element = {
      elementType: ElementType.FILE,
      elementId: "",
      fileElement: {
        fileName: fileName || _fileName,
        folderId,
        "filePath": path,
        "fileSize": fileSize.toString()
      }
    };
    return element;
  }
  static async video(filePath, fileName = "", diyThumbPath = "", videotype = viedo_type.VIDEO_FORMAT_MP4) {
    const {
      fileName: _fileName,
      path,
      fileSize,
      md5
    } = await NTQQFileApi.uploadFile(filePath, ElementType.VIDEO);
    if (fileSize === 0) {
      throw "文件异常，大小为0";
    }
    let thumb = path.replace(`${path$1.sep}Ori${path$1.sep}`, `${path$1.sep}Thumb${path$1.sep}`);
    thumb = path$1.dirname(thumb);
    let videoInfo = {
      width: 1920,
      height: 1080,
      time: 15,
      format: "mp4",
      size: fileSize,
      filePath
    };
    try {
      videoInfo = await getVideoInfo(path);
    } catch (e) {
      logError("获取视频信息失败", e);
    }
    const createThumb = new Promise((resolve, reject) => {
      const thumbFileName = `${md5}_0.png`;
      const thumbPath2 = path$1.join(thumb, thumbFileName);
      ffmpeg(filePath).on("end", () => {
      }).on("error", (err) => {
        logDebug("获取视频封面失败，使用默认封面", err);
        if (diyThumbPath) {
          promises.copyFile(diyThumbPath, thumbPath2).then(() => {
            resolve(thumbPath2);
          }).catch(reject);
        } else {
          promises.writeFile(thumbPath2, defaultVideoThumb).then(() => {
            resolve(thumbPath2);
          }).catch(reject);
        }
      }).screenshots({
        timestamps: [0],
        filename: thumbFileName,
        folder: thumb,
        size: videoInfo.width + "x" + videoInfo.height
      }).on("end", () => {
        resolve(thumbPath2);
      });
    });
    const thumbPath = /* @__PURE__ */ new Map();
    const _thumbPath = await createThumb;
    const thumbSize = (await promises.stat(_thumbPath)).size;
    thumbPath.set(0, _thumbPath);
    const thumbMd5 = await calculateFileMD5(_thumbPath);
    const element = {
      elementType: ElementType.VIDEO,
      elementId: "",
      videoElement: {
        fileName: fileName || _fileName,
        filePath: path,
        videoMd5: md5,
        thumbMd5,
        fileTime: videoInfo.time,
        thumbPath,
        thumbSize,
        thumbWidth: videoInfo.width,
        thumbHeight: videoInfo.height,
        fileSize: "" + fileSize
        //fileFormat: videotype
        // fileUuid: "",
        // transferStatus: 0,
        // progress: 0,
        // invalidState: 0,
        // fileSubId: "",
        // fileBizId: null,
        // originVideoMd5: "",
        // fileFormat: 2,
        // import_rich_media_context: null,
        // sourceVideoCodecFormat: 2
      }
    };
    return element;
  }
  static async ptt(pttPath) {
    const {
      converted,
      path: silkPath,
      duration
    } = await encodeSilk(pttPath);
    if (!silkPath) {
      throw "语音转换失败, 请检查语音文件是否正常";
    }
    const {
      md5,
      fileName,
      path,
      fileSize
    } = await NTQQFileApi.uploadFile(silkPath, ElementType.PTT);
    if (fileSize === 0) {
      throw "文件异常，大小为0";
    }
    if (converted) {
      promises.unlink(silkPath).then();
    }
    return {
      elementType: ElementType.PTT,
      elementId: "",
      pttElement: {
        fileName,
        filePath: path,
        md5HexStr: md5,
        fileSize,
        // duration: Math.max(1, Math.round(fileSize / 1024 / 3)), // 一秒钟大概是3kb大小, 小于1秒的按1秒算
        duration: duration || 1,
        formatType: 1,
        voiceType: 1,
        voiceChangeType: 0,
        canConvert2Text: true,
        waveAmplitudes: [0, 18, 9, 23, 16, 17, 16, 15, 44, 17, 24, 20, 14, 15, 17],
        fileSubId: "",
        playState: 1,
        autoConvertText: 0
      }
    };
  }
  // NodeIQQNTWrapperSession sendMsg  [
  //   "0",
  //   {
  //     "peerUid": "u_e_RIxgTs2NaJ68h0PwOPSg",
  //     "chatType": 1,
  //     "guildId": ""
  //   },
  //   [
  //     {
  //       "elementId": "0",
  //       "elementType": 6,
  //       "faceElement": {
  //         "faceIndex": 0,
  //         "faceType": 5,
  //         "msgType": 0,
  //         "pokeType": 1,
  //         "pokeStrength": 0
  //       }
  //     }
  //   ],
  //   {}
  // ]
  static face(faceId) {
    const sysFaces = faceConfig.sysface;
    const face = sysFaces.find((face2) => face2.QSid === faceId.toString());
    faceId = parseInt(faceId.toString());
    let faceType = 1;
    if (faceId >= 222) {
      faceType = 2;
    }
    if (face.AniStickerType) {
      faceType = 3;
    }
    return {
      elementType: ElementType.FACE,
      elementId: "",
      faceElement: {
        faceIndex: faceId,
        faceType,
        faceText: face.QDes,
        stickerId: face.AniStickerId,
        stickerType: face.AniStickerType,
        packId: face.AniStickerPackId,
        sourceType: 1
      }
    };
  }
  static mface(emojiPackageId, emojiId, key, faceName) {
    return {
      elementType: ElementType.MFACE,
      marketFaceElement: {
        emojiPackageId,
        emojiId,
        key,
        faceName: faceName || mFaceCache.get(emojiId) || "[商城表情]"
      }
    };
  }
  static dice(resultId) {
    return {
      elementType: ElementType.FACE,
      elementId: "",
      faceElement: {
        faceIndex: FaceIndex.dice,
        faceType: FaceType.dice,
        "faceText": "[骰子]",
        "packId": "1",
        "stickerId": "33",
        "sourceType": 1,
        "stickerType": 2,
        // resultId: resultId.toString(),
        "surpriseId": ""
        // "randomType": 1,
      }
    };
  }
  // 猜拳(石头剪刀布)表情
  static rps(resultId) {
    return {
      elementType: ElementType.FACE,
      elementId: "",
      faceElement: {
        "faceIndex": FaceIndex.RPS,
        "faceText": "[包剪锤]",
        "faceType": 3,
        "packId": "1",
        "stickerId": "34",
        "sourceType": 1,
        "stickerType": 2,
        // 'resultId': resultId.toString(),
        "surpriseId": ""
        // "randomType": 1,
      }
    };
  }
  static ark(data) {
    if (typeof data !== "string") {
      data = JSON.stringify(data);
    }
    return {
      elementType: ElementType.ARK,
      elementId: "",
      arkElement: {
        bytesData: data,
        linkInfo: null,
        subElementType: null
      }
    };
  }
  static markdown(content) {
    return {
      elementType: ElementType.MARKDOWN,
      elementId: "",
      markdownElement: {
        content
      }
    };
  }
  static async miniapp() {
    let ret = await SignMiniApp({
      prompt: "Bot Test",
      title: "Bot Test",
      preview: "https://tianquan.gtimg.cn/qqAIAgent/item/7/square.png",
      jumpUrl: "https://www.bilibili.com/",
      tag: "Bot Test",
      tagIcon: "https://tianquan.gtimg.cn/shoal/qqAIAgent/3e9d70c9-d98c-45b8-80b4-79d82971b514.png",
      source: "Bot Test",
      sourcelogo: "https://tianquan.gtimg.cn/shoal/qqAIAgent/3e9d70c9-d98c-45b8-80b4-79d82971b514.png"
    });
    return {
      elementType: ElementType.ARK,
      elementId: "",
      arkElement: {
        bytesData: ret,
        linkInfo: null,
        subElementType: null
      }
    };
  }
}

var dist = {exports: {}};

var queue = {exports: {}};

var inherits_browser = {exports: {}};

if (typeof Object.create === 'function') {
  // implementation from standard node.js 'util' module
  inherits_browser.exports = function inherits(ctor, superCtor) {
    if (superCtor) {
      ctor.super_ = superCtor;
      ctor.prototype = Object.create(superCtor.prototype, {
        constructor: {
          value: ctor,
          enumerable: false,
          writable: true,
          configurable: true
        }
      });
    }
  };
} else {
  // old school shim for old browsers
  inherits_browser.exports = function inherits(ctor, superCtor) {
    if (superCtor) {
      ctor.super_ = superCtor;
      var TempCtor = function () {};
      TempCtor.prototype = superCtor.prototype;
      ctor.prototype = new TempCtor();
      ctor.prototype.constructor = ctor;
    }
  };
}

var inherits_browserExports = inherits_browser.exports;

var inherits = inherits_browserExports;
var EventEmitter$1 = require$$1.EventEmitter;
queue.exports = Queue;
queue.exports.default = Queue;
function Queue(options) {
  if (!(this instanceof Queue)) {
    return new Queue(options);
  }
  EventEmitter$1.call(this);
  options = options || {};
  this.concurrency = options.concurrency || Infinity;
  this.timeout = options.timeout || 0;
  this.autostart = options.autostart || false;
  this.results = options.results || null;
  this.pending = 0;
  this.session = 0;
  this.running = false;
  this.jobs = [];
  this.timers = {};
}
inherits(Queue, EventEmitter$1);
var arrayMethods = ['pop', 'shift', 'indexOf', 'lastIndexOf'];
arrayMethods.forEach(function (method) {
  Queue.prototype[method] = function () {
    return Array.prototype[method].apply(this.jobs, arguments);
  };
});
Queue.prototype.slice = function (begin, end) {
  this.jobs = this.jobs.slice(begin, end);
  return this;
};
Queue.prototype.reverse = function () {
  this.jobs.reverse();
  return this;
};
var arrayAddMethods = ['push', 'unshift', 'splice'];
arrayAddMethods.forEach(function (method) {
  Queue.prototype[method] = function () {
    var methodResult = Array.prototype[method].apply(this.jobs, arguments);
    if (this.autostart) {
      this.start();
    }
    return methodResult;
  };
});
Object.defineProperty(Queue.prototype, 'length', {
  get: function () {
    return this.pending + this.jobs.length;
  }
});
Queue.prototype.start = function (cb) {
  if (cb) {
    callOnErrorOrEnd.call(this, cb);
  }
  this.running = true;
  if (this.pending >= this.concurrency) {
    return;
  }
  if (this.jobs.length === 0) {
    if (this.pending === 0) {
      done.call(this);
    }
    return;
  }
  var self = this;
  var job = this.jobs.shift();
  var once = true;
  var session = this.session;
  var timeoutId = null;
  var didTimeout = false;
  var resultIndex = null;
  var timeout = job.hasOwnProperty('timeout') ? job.timeout : this.timeout;
  function next(err, result) {
    if (once && self.session === session) {
      once = false;
      self.pending--;
      if (timeoutId !== null) {
        delete self.timers[timeoutId];
        clearTimeout(timeoutId);
      }
      if (err) {
        self.emit('error', err, job);
      } else if (didTimeout === false) {
        if (resultIndex !== null) {
          self.results[resultIndex] = Array.prototype.slice.call(arguments, 1);
        }
        self.emit('success', result, job);
      }
      if (self.session === session) {
        if (self.pending === 0 && self.jobs.length === 0) {
          done.call(self);
        } else if (self.running) {
          self.start();
        }
      }
    }
  }
  if (timeout) {
    timeoutId = setTimeout(function () {
      didTimeout = true;
      if (self.listeners('timeout').length > 0) {
        self.emit('timeout', next, job);
      } else {
        next();
      }
    }, timeout);
    this.timers[timeoutId] = timeoutId;
  }
  if (this.results) {
    resultIndex = this.results.length;
    this.results[resultIndex] = null;
  }
  this.pending++;
  self.emit('start', job);
  var promise = job(next);
  if (promise && promise.then && typeof promise.then === 'function') {
    promise.then(function (result) {
      return next(null, result);
    }).catch(function (err) {
      return next(err || true);
    });
  }
  if (this.running && this.jobs.length > 0) {
    this.start();
  }
};
Queue.prototype.stop = function () {
  this.running = false;
};
Queue.prototype.end = function (err) {
  clearTimers.call(this);
  this.jobs.length = 0;
  this.pending = 0;
  done.call(this, err);
};
function clearTimers() {
  for (var key in this.timers) {
    var timeoutId = this.timers[key];
    delete this.timers[key];
    clearTimeout(timeoutId);
  }
}
function callOnErrorOrEnd(cb) {
  var self = this;
  this.on('error', onerror);
  this.on('end', onend);
  function onerror(err) {
    self.end(err);
  }
  function onend(err) {
    self.removeListener('error', onerror);
    self.removeListener('end', onend);
    cb(err, this.results);
  }
}
function done(err) {
  this.session++;
  this.running = false;
  this.emit('end', err);
}

var queueExports = queue.exports;

var types$1 = {};

var bmp = {};

var utils$1 = {};

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.findBox = exports.readUInt = exports.readUInt32LE = exports.readUInt32BE = exports.readInt32LE = exports.readUInt24LE = exports.readUInt16LE = exports.readUInt16BE = exports.readInt16LE = exports.toHexString = exports.toUTF8String = void 0;
	const decoder = new TextDecoder();
	const toUTF8String = (input, start = 0, end = input.length) => decoder.decode(input.slice(start, end));
	exports.toUTF8String = toUTF8String;
	const toHexString = (input, start = 0, end = input.length) => input.slice(start, end).reduce((memo, i) => memo + ('0' + i.toString(16)).slice(-2), '');
	exports.toHexString = toHexString;
	const readInt16LE = (input, offset = 0) => {
	  const val = input[offset] + input[offset + 1] * 2 ** 8;
	  return val | (val & 2 ** 15) * 0x1fffe;
	};
	exports.readInt16LE = readInt16LE;
	const readUInt16BE = (input, offset = 0) => input[offset] * 2 ** 8 + input[offset + 1];
	exports.readUInt16BE = readUInt16BE;
	const readUInt16LE = (input, offset = 0) => input[offset] + input[offset + 1] * 2 ** 8;
	exports.readUInt16LE = readUInt16LE;
	const readUInt24LE = (input, offset = 0) => input[offset] + input[offset + 1] * 2 ** 8 + input[offset + 2] * 2 ** 16;
	exports.readUInt24LE = readUInt24LE;
	const readInt32LE = (input, offset = 0) => input[offset] + input[offset + 1] * 2 ** 8 + input[offset + 2] * 2 ** 16 + (input[offset + 3] << 24);
	exports.readInt32LE = readInt32LE;
	const readUInt32BE = (input, offset = 0) => input[offset] * 2 ** 24 + input[offset + 1] * 2 ** 16 + input[offset + 2] * 2 ** 8 + input[offset + 3];
	exports.readUInt32BE = readUInt32BE;
	const readUInt32LE = (input, offset = 0) => input[offset] + input[offset + 1] * 2 ** 8 + input[offset + 2] * 2 ** 16 + input[offset + 3] * 2 ** 24;
	exports.readUInt32LE = readUInt32LE;
	// Abstract reading multi-byte unsigned integers
	const methods = {
	  readUInt16BE: exports.readUInt16BE,
	  readUInt16LE: exports.readUInt16LE,
	  readUInt32BE: exports.readUInt32BE,
	  readUInt32LE: exports.readUInt32LE
	};
	function readUInt(input, bits, offset, isBigEndian) {
	  offset = offset || 0;
	  const endian = isBigEndian ? 'BE' : 'LE';
	  const methodName = 'readUInt' + bits + endian;
	  return methods[methodName](input, offset);
	}
	exports.readUInt = readUInt;
	function readBox(buffer, offset) {
	  if (buffer.length - offset < 4) return;
	  const boxSize = (0, exports.readUInt32BE)(buffer, offset);
	  if (buffer.length - offset < boxSize) return;
	  return {
	    name: (0, exports.toUTF8String)(buffer, 4 + offset, 8 + offset),
	    offset,
	    size: boxSize
	  };
	}
	function findBox(buffer, boxName, offset) {
	  while (offset < buffer.length) {
	    const box = readBox(buffer, offset);
	    if (!box) break;
	    if (box.name === boxName) return box;
	    offset += box.size;
	  }
	}
	exports.findBox = findBox; 
} (utils$1));

Object.defineProperty(bmp, "__esModule", {
  value: true
});
bmp.BMP = void 0;
const utils_1$h = utils$1;
bmp.BMP = {
  validate: input => (0, utils_1$h.toUTF8String)(input, 0, 2) === 'BM',
  calculate: input => ({
    height: Math.abs((0, utils_1$h.readInt32LE)(input, 22)),
    width: (0, utils_1$h.readUInt32LE)(input, 18)
  })
};

var cur = {};

var ico = {};

Object.defineProperty(ico, "__esModule", {
  value: true
});
ico.ICO = void 0;
const utils_1$g = utils$1;
const TYPE_ICON = 1;
/**
 * ICON Header
 *
 * | Offset | Size | Purpose |
 * | 0	    | 2    | Reserved. Must always be 0.  |
 * | 2      | 2    | Image type: 1 for icon (.ICO) image, 2 for cursor (.CUR) image. Other values are invalid. |
 * | 4      | 2    | Number of images in the file. |
 *
 */
const SIZE_HEADER$1 = 2 + 2 + 2; // 6
/**
 * Image Entry
 *
 * | Offset | Size | Purpose |
 * | 0	    | 1    | Image width in pixels. Can be any number between 0 and 255. Value 0 means width is 256 pixels. |
 * | 1      | 1    | Image height in pixels. Can be any number between 0 and 255. Value 0 means height is 256 pixels. |
 * | 2      | 1    | Number of colors in the color palette. Should be 0 if the image does not use a color palette. |
 * | 3      | 1    | Reserved. Should be 0. |
 * | 4      | 2    | ICO format: Color planes. Should be 0 or 1. |
 * |        |      | CUR format: The horizontal coordinates of the hotspot in number of pixels from the left. |
 * | 6      | 2    | ICO format: Bits per pixel. |
 * |        |      | CUR format: The vertical coordinates of the hotspot in number of pixels from the top. |
 * | 8      | 4    | The size of the image's data in bytes |
 * | 12     | 4    | The offset of BMP or PNG data from the beginning of the ICO/CUR file |
 *
 */
const SIZE_IMAGE_ENTRY = 1 + 1 + 1 + 1 + 2 + 2 + 4 + 4; // 16
function getSizeFromOffset(input, offset) {
  const value = input[offset];
  return value === 0 ? 256 : value;
}
function getImageSize$1(input, imageIndex) {
  const offset = SIZE_HEADER$1 + imageIndex * SIZE_IMAGE_ENTRY;
  return {
    height: getSizeFromOffset(input, offset + 1),
    width: getSizeFromOffset(input, offset)
  };
}
ico.ICO = {
  validate(input) {
    const reserved = (0, utils_1$g.readUInt16LE)(input, 0);
    const imageCount = (0, utils_1$g.readUInt16LE)(input, 4);
    if (reserved !== 0 || imageCount === 0) return false;
    const imageType = (0, utils_1$g.readUInt16LE)(input, 2);
    return imageType === TYPE_ICON;
  },
  calculate(input) {
    const nbImages = (0, utils_1$g.readUInt16LE)(input, 4);
    const imageSize = getImageSize$1(input, 0);
    if (nbImages === 1) return imageSize;
    const imgs = [imageSize];
    for (let imageIndex = 1; imageIndex < nbImages; imageIndex += 1) {
      imgs.push(getImageSize$1(input, imageIndex));
    }
    return {
      height: imageSize.height,
      images: imgs,
      width: imageSize.width
    };
  }
};

Object.defineProperty(cur, "__esModule", {
  value: true
});
cur.CUR = void 0;
const ico_1$1 = ico;
const utils_1$f = utils$1;
const TYPE_CURSOR = 2;
cur.CUR = {
  validate(input) {
    const reserved = (0, utils_1$f.readUInt16LE)(input, 0);
    const imageCount = (0, utils_1$f.readUInt16LE)(input, 4);
    if (reserved !== 0 || imageCount === 0) return false;
    const imageType = (0, utils_1$f.readUInt16LE)(input, 2);
    return imageType === TYPE_CURSOR;
  },
  calculate: input => ico_1$1.ICO.calculate(input)
};

var dds = {};

Object.defineProperty(dds, "__esModule", {
  value: true
});
dds.DDS = void 0;
const utils_1$e = utils$1;
dds.DDS = {
  validate: input => (0, utils_1$e.readUInt32LE)(input, 0) === 0x20534444,
  calculate: input => ({
    height: (0, utils_1$e.readUInt32LE)(input, 12),
    width: (0, utils_1$e.readUInt32LE)(input, 16)
  })
};

var gif = {};

Object.defineProperty(gif, "__esModule", {
  value: true
});
gif.GIF = void 0;
const utils_1$d = utils$1;
const gifRegexp = /^GIF8[79]a/;
gif.GIF = {
  validate: input => gifRegexp.test((0, utils_1$d.toUTF8String)(input, 0, 6)),
  calculate: input => ({
    height: (0, utils_1$d.readUInt16LE)(input, 8),
    width: (0, utils_1$d.readUInt16LE)(input, 6)
  })
};

var heif = {};

Object.defineProperty(heif, "__esModule", {
  value: true
});
heif.HEIF = void 0;
const utils_1$c = utils$1;
const brandMap = {
  avif: 'avif',
  mif1: 'heif',
  msf1: 'heif',
  // hief-sequence
  heic: 'heic',
  heix: 'heic',
  hevc: 'heic',
  // heic-sequence
  hevx: 'heic' // heic-sequence
};
heif.HEIF = {
  validate(buffer) {
    const ftype = (0, utils_1$c.toUTF8String)(buffer, 4, 8);
    const brand = (0, utils_1$c.toUTF8String)(buffer, 8, 12);
    return 'ftyp' === ftype && brand in brandMap;
  },
  calculate(buffer) {
    // Based on https://nokiatech.github.io/heif/technical.html
    const metaBox = (0, utils_1$c.findBox)(buffer, 'meta', 0);
    const iprpBox = metaBox && (0, utils_1$c.findBox)(buffer, 'iprp', metaBox.offset + 12);
    const ipcoBox = iprpBox && (0, utils_1$c.findBox)(buffer, 'ipco', iprpBox.offset + 8);
    const ispeBox = ipcoBox && (0, utils_1$c.findBox)(buffer, 'ispe', ipcoBox.offset + 8);
    if (ispeBox) {
      return {
        height: (0, utils_1$c.readUInt32BE)(buffer, ispeBox.offset + 16),
        width: (0, utils_1$c.readUInt32BE)(buffer, ispeBox.offset + 12),
        type: (0, utils_1$c.toUTF8String)(buffer, 8, 12)
      };
    }
    throw new TypeError('Invalid HEIF, no size found');
  }
};

var icns = {};

Object.defineProperty(icns, "__esModule", {
  value: true
});
icns.ICNS = void 0;
const utils_1$b = utils$1;
/**
 * ICNS Header
 *
 * | Offset | Size | Purpose                                                |
 * | 0	    | 4    | Magic literal, must be "icns" (0x69, 0x63, 0x6e, 0x73) |
 * | 4      | 4    | Length of file, in bytes, msb first.                   |
 *
 */
const SIZE_HEADER = 4 + 4; // 8
const FILE_LENGTH_OFFSET = 4; // MSB => BIG ENDIAN
/**
 * Image Entry
 *
 * | Offset | Size | Purpose                                                          |
 * | 0	    | 4    | Icon type, see OSType below.                                     |
 * | 4      | 4    | Length of data, in bytes (including type and length), msb first. |
 * | 8      | n    | Icon data                                                        |
 */
const ENTRY_LENGTH_OFFSET = 4; // MSB => BIG ENDIAN
const ICON_TYPE_SIZE = {
  ICON: 32,
  'ICN#': 32,
  // m => 16 x 16
  'icm#': 16,
  icm4: 16,
  icm8: 16,
  // s => 16 x 16
  'ics#': 16,
  ics4: 16,
  ics8: 16,
  is32: 16,
  s8mk: 16,
  icp4: 16,
  // l => 32 x 32
  icl4: 32,
  icl8: 32,
  il32: 32,
  l8mk: 32,
  icp5: 32,
  ic11: 32,
  // h => 48 x 48
  ich4: 48,
  ich8: 48,
  ih32: 48,
  h8mk: 48,
  // . => 64 x 64
  icp6: 64,
  ic12: 32,
  // t => 128 x 128
  it32: 128,
  t8mk: 128,
  ic07: 128,
  // . => 256 x 256
  ic08: 256,
  ic13: 256,
  // . => 512 x 512
  ic09: 512,
  ic14: 512,
  // . => 1024 x 1024
  ic10: 1024
};
function readImageHeader(input, imageOffset) {
  const imageLengthOffset = imageOffset + ENTRY_LENGTH_OFFSET;
  return [(0, utils_1$b.toUTF8String)(input, imageOffset, imageLengthOffset), (0, utils_1$b.readUInt32BE)(input, imageLengthOffset)];
}
function getImageSize(type) {
  const size = ICON_TYPE_SIZE[type];
  return {
    width: size,
    height: size,
    type
  };
}
icns.ICNS = {
  validate: input => (0, utils_1$b.toUTF8String)(input, 0, 4) === 'icns',
  calculate(input) {
    const inputLength = input.length;
    const fileLength = (0, utils_1$b.readUInt32BE)(input, FILE_LENGTH_OFFSET);
    let imageOffset = SIZE_HEADER;
    let imageHeader = readImageHeader(input, imageOffset);
    let imageSize = getImageSize(imageHeader[0]);
    imageOffset += imageHeader[1];
    if (imageOffset === fileLength) return imageSize;
    const result = {
      height: imageSize.height,
      images: [imageSize],
      width: imageSize.width
    };
    while (imageOffset < fileLength && imageOffset < inputLength) {
      imageHeader = readImageHeader(input, imageOffset);
      imageSize = getImageSize(imageHeader[0]);
      imageOffset += imageHeader[1];
      result.images.push(imageSize);
    }
    return result;
  }
};

var j2c = {};

Object.defineProperty(j2c, "__esModule", {
  value: true
});
j2c.J2C = void 0;
const utils_1$a = utils$1;
j2c.J2C = {
  // TODO: this doesn't seem right. SIZ marker doesn't have to be right after the SOC
  validate: input => (0, utils_1$a.toHexString)(input, 0, 4) === 'ff4fff51',
  calculate: input => ({
    height: (0, utils_1$a.readUInt32BE)(input, 12),
    width: (0, utils_1$a.readUInt32BE)(input, 8)
  })
};

var jp2 = {};

Object.defineProperty(jp2, "__esModule", {
  value: true
});
jp2.JP2 = void 0;
const utils_1$9 = utils$1;
jp2.JP2 = {
  validate(input) {
    if ((0, utils_1$9.readUInt32BE)(input, 4) !== 0x6a502020 || (0, utils_1$9.readUInt32BE)(input, 0) < 1) return false;
    const ftypBox = (0, utils_1$9.findBox)(input, 'ftyp', 0);
    if (!ftypBox) return false;
    return (0, utils_1$9.readUInt32BE)(input, ftypBox.offset + 4) === 0x66747970;
  },
  calculate(input) {
    const jp2hBox = (0, utils_1$9.findBox)(input, 'jp2h', 0);
    const ihdrBox = jp2hBox && (0, utils_1$9.findBox)(input, 'ihdr', jp2hBox.offset + 8);
    if (ihdrBox) {
      return {
        height: (0, utils_1$9.readUInt32BE)(input, ihdrBox.offset + 8),
        width: (0, utils_1$9.readUInt32BE)(input, ihdrBox.offset + 12)
      };
    }
    throw new TypeError('Unsupported JPEG 2000 format');
  }
};

var jpg = {};

// NOTE: we only support baseline and progressive JPGs here
// due to the structure of the loader class, we only get a buffer
// with a maximum size of 4096 bytes. so if the SOF marker is outside
// if this range we can't detect the file size correctly.
Object.defineProperty(jpg, "__esModule", {
  value: true
});
jpg.JPG = void 0;
const utils_1$8 = utils$1;
const EXIF_MARKER = '45786966';
const APP1_DATA_SIZE_BYTES = 2;
const EXIF_HEADER_BYTES = 6;
const TIFF_BYTE_ALIGN_BYTES = 2;
const BIG_ENDIAN_BYTE_ALIGN = '4d4d';
const LITTLE_ENDIAN_BYTE_ALIGN = '4949';
// Each entry is exactly 12 bytes
const IDF_ENTRY_BYTES = 12;
const NUM_DIRECTORY_ENTRIES_BYTES = 2;
function isEXIF(input) {
  return (0, utils_1$8.toHexString)(input, 2, 6) === EXIF_MARKER;
}
function extractSize(input, index) {
  return {
    height: (0, utils_1$8.readUInt16BE)(input, index),
    width: (0, utils_1$8.readUInt16BE)(input, index + 2)
  };
}
function extractOrientation(exifBlock, isBigEndian) {
  // TODO: assert that this contains 0x002A
  // let STATIC_MOTOROLA_TIFF_HEADER_BYTES = 2
  // let TIFF_IMAGE_FILE_DIRECTORY_BYTES = 4
  // TODO: derive from TIFF_IMAGE_FILE_DIRECTORY_BYTES
  const idfOffset = 8;
  // IDF osset works from right after the header bytes
  // (so the offset includes the tiff byte align)
  const offset = EXIF_HEADER_BYTES + idfOffset;
  const idfDirectoryEntries = (0, utils_1$8.readUInt)(exifBlock, 16, offset, isBigEndian);
  for (let directoryEntryNumber = 0; directoryEntryNumber < idfDirectoryEntries; directoryEntryNumber++) {
    const start = offset + NUM_DIRECTORY_ENTRIES_BYTES + directoryEntryNumber * IDF_ENTRY_BYTES;
    const end = start + IDF_ENTRY_BYTES;
    // Skip on corrupt EXIF blocks
    if (start > exifBlock.length) {
      return;
    }
    const block = exifBlock.slice(start, end);
    const tagNumber = (0, utils_1$8.readUInt)(block, 16, 0, isBigEndian);
    // 0x0112 (decimal: 274) is the `orientation` tag ID
    if (tagNumber === 274) {
      const dataFormat = (0, utils_1$8.readUInt)(block, 16, 2, isBigEndian);
      if (dataFormat !== 3) {
        return;
      }
      // unsinged int has 2 bytes per component
      // if there would more than 4 bytes in total it's a pointer
      const numberOfComponents = (0, utils_1$8.readUInt)(block, 32, 4, isBigEndian);
      if (numberOfComponents !== 1) {
        return;
      }
      return (0, utils_1$8.readUInt)(block, 16, 8, isBigEndian);
    }
  }
}
function validateExifBlock(input, index) {
  // Skip APP1 Data Size
  const exifBlock = input.slice(APP1_DATA_SIZE_BYTES, index);
  // Consider byte alignment
  const byteAlign = (0, utils_1$8.toHexString)(exifBlock, EXIF_HEADER_BYTES, EXIF_HEADER_BYTES + TIFF_BYTE_ALIGN_BYTES);
  // Ignore Empty EXIF. Validate byte alignment
  const isBigEndian = byteAlign === BIG_ENDIAN_BYTE_ALIGN;
  const isLittleEndian = byteAlign === LITTLE_ENDIAN_BYTE_ALIGN;
  if (isBigEndian || isLittleEndian) {
    return extractOrientation(exifBlock, isBigEndian);
  }
}
function validateInput(input, index) {
  // index should be within buffer limits
  if (index > input.length) {
    throw new TypeError('Corrupt JPG, exceeded buffer limits');
  }
}
jpg.JPG = {
  validate: input => (0, utils_1$8.toHexString)(input, 0, 2) === 'ffd8',
  calculate(input) {
    // Skip 4 chars, they are for signature
    input = input.slice(4);
    let orientation;
    let next;
    while (input.length) {
      // read length of the next block
      const i = (0, utils_1$8.readUInt16BE)(input, 0);
      // Every JPEG block must begin with a 0xFF
      if (input[i] !== 0xff) {
        input = input.slice(1);
        continue;
      }
      if (isEXIF(input)) {
        orientation = validateExifBlock(input, i);
      }
      // ensure correct format
      validateInput(input, i);
      // 0xFFC0 is baseline standard(SOF)
      // 0xFFC1 is baseline optimized(SOF)
      // 0xFFC2 is progressive(SOF2)
      next = input[i + 1];
      if (next === 0xc0 || next === 0xc1 || next === 0xc2) {
        const size = extractSize(input, i + 5);
        // TODO: is orientation=0 a valid answer here?
        if (!orientation) {
          return size;
        }
        return {
          height: size.height,
          orientation,
          width: size.width
        };
      }
      // move to the next block
      input = input.slice(i + 2);
    }
    throw new TypeError('Invalid JPG, no size found');
  }
};

var ktx = {};

Object.defineProperty(ktx, "__esModule", {
  value: true
});
ktx.KTX = void 0;
const utils_1$7 = utils$1;
ktx.KTX = {
  validate: input => {
    const signature = (0, utils_1$7.toUTF8String)(input, 1, 7);
    return ['KTX 11', 'KTX 20'].includes(signature);
  },
  calculate: input => {
    const type = input[5] === 0x31 ? 'ktx' : 'ktx2';
    const offset = type === 'ktx' ? 36 : 20;
    return {
      height: (0, utils_1$7.readUInt32LE)(input, offset + 4),
      width: (0, utils_1$7.readUInt32LE)(input, offset),
      type
    };
  }
};

var png = {};

Object.defineProperty(png, "__esModule", {
  value: true
});
png.PNG = void 0;
const utils_1$6 = utils$1;
const pngSignature = 'PNG\r\n\x1a\n';
const pngImageHeaderChunkName = 'IHDR';
// Used to detect "fried" png's: http://www.jongware.com/pngdefry.html
const pngFriedChunkName = 'CgBI';
png.PNG = {
  validate(input) {
    if (pngSignature === (0, utils_1$6.toUTF8String)(input, 1, 8)) {
      let chunkName = (0, utils_1$6.toUTF8String)(input, 12, 16);
      if (chunkName === pngFriedChunkName) {
        chunkName = (0, utils_1$6.toUTF8String)(input, 28, 32);
      }
      if (chunkName !== pngImageHeaderChunkName) {
        throw new TypeError('Invalid PNG');
      }
      return true;
    }
    return false;
  },
  calculate(input) {
    if ((0, utils_1$6.toUTF8String)(input, 12, 16) === pngFriedChunkName) {
      return {
        height: (0, utils_1$6.readUInt32BE)(input, 36),
        width: (0, utils_1$6.readUInt32BE)(input, 32)
      };
    }
    return {
      height: (0, utils_1$6.readUInt32BE)(input, 20),
      width: (0, utils_1$6.readUInt32BE)(input, 16)
    };
  }
};

var pnm = {};

Object.defineProperty(pnm, "__esModule", {
  value: true
});
pnm.PNM = void 0;
const utils_1$5 = utils$1;
const PNMTypes = {
  P1: 'pbm/ascii',
  P2: 'pgm/ascii',
  P3: 'ppm/ascii',
  P4: 'pbm',
  P5: 'pgm',
  P6: 'ppm',
  P7: 'pam',
  PF: 'pfm'
};
const handlers$1 = {
  default: lines => {
    let dimensions = [];
    while (lines.length > 0) {
      const line = lines.shift();
      if (line[0] === '#') {
        continue;
      }
      dimensions = line.split(' ');
      break;
    }
    if (dimensions.length === 2) {
      return {
        height: parseInt(dimensions[1], 10),
        width: parseInt(dimensions[0], 10)
      };
    } else {
      throw new TypeError('Invalid PNM');
    }
  },
  pam: lines => {
    const size = {};
    while (lines.length > 0) {
      const line = lines.shift();
      if (line.length > 16 || line.charCodeAt(0) > 128) {
        continue;
      }
      const [key, value] = line.split(' ');
      if (key && value) {
        size[key.toLowerCase()] = parseInt(value, 10);
      }
      if (size.height && size.width) {
        break;
      }
    }
    if (size.height && size.width) {
      return {
        height: size.height,
        width: size.width
      };
    } else {
      throw new TypeError('Invalid PAM');
    }
  }
};
pnm.PNM = {
  validate: input => (0, utils_1$5.toUTF8String)(input, 0, 2) in PNMTypes,
  calculate(input) {
    const signature = (0, utils_1$5.toUTF8String)(input, 0, 2);
    const type = PNMTypes[signature];
    // TODO: this probably generates garbage. move to a stream based parser
    const lines = (0, utils_1$5.toUTF8String)(input, 3).split(/[\r\n]+/);
    const handler = handlers$1[type] || handlers$1.default;
    return handler(lines);
  }
};

var psd = {};

Object.defineProperty(psd, "__esModule", {
  value: true
});
psd.PSD = void 0;
const utils_1$4 = utils$1;
psd.PSD = {
  validate: input => (0, utils_1$4.toUTF8String)(input, 0, 4) === '8BPS',
  calculate: input => ({
    height: (0, utils_1$4.readUInt32BE)(input, 14),
    width: (0, utils_1$4.readUInt32BE)(input, 18)
  })
};

var svg = {};

Object.defineProperty(svg, "__esModule", {
  value: true
});
svg.SVG = void 0;
const utils_1$3 = utils$1;
const svgReg = /<svg\s([^>"']|"[^"]*"|'[^']*')*>/;
const extractorRegExps = {
  height: /\sheight=(['"])([^%]+?)\1/,
  root: svgReg,
  viewbox: /\sviewBox=(['"])(.+?)\1/i,
  width: /\swidth=(['"])([^%]+?)\1/
};
const INCH_CM = 2.54;
const units = {
  in: 96,
  cm: 96 / INCH_CM,
  em: 16,
  ex: 8,
  m: 96 / INCH_CM * 100,
  mm: 96 / INCH_CM / 10,
  pc: 96 / 72 / 12,
  pt: 96 / 72,
  px: 1
};
const unitsReg = new RegExp(`^([0-9.]+(?:e\\d+)?)(${Object.keys(units).join('|')})?$`);
function parseLength(len) {
  const m = unitsReg.exec(len);
  if (!m) {
    return undefined;
  }
  return Math.round(Number(m[1]) * (units[m[2]] || 1));
}
function parseViewbox(viewbox) {
  const bounds = viewbox.split(' ');
  return {
    height: parseLength(bounds[3]),
    width: parseLength(bounds[2])
  };
}
function parseAttributes(root) {
  const width = root.match(extractorRegExps.width);
  const height = root.match(extractorRegExps.height);
  const viewbox = root.match(extractorRegExps.viewbox);
  return {
    height: height && parseLength(height[2]),
    viewbox: viewbox && parseViewbox(viewbox[2]),
    width: width && parseLength(width[2])
  };
}
function calculateByDimensions(attrs) {
  return {
    height: attrs.height,
    width: attrs.width
  };
}
function calculateByViewbox(attrs, viewbox) {
  const ratio = viewbox.width / viewbox.height;
  if (attrs.width) {
    return {
      height: Math.floor(attrs.width / ratio),
      width: attrs.width
    };
  }
  if (attrs.height) {
    return {
      height: attrs.height,
      width: Math.floor(attrs.height * ratio)
    };
  }
  return {
    height: viewbox.height,
    width: viewbox.width
  };
}
svg.SVG = {
  // Scan only the first kilo-byte to speed up the check on larger files
  validate: input => svgReg.test((0, utils_1$3.toUTF8String)(input, 0, 1000)),
  calculate(input) {
    const root = (0, utils_1$3.toUTF8String)(input).match(extractorRegExps.root);
    if (root) {
      const attrs = parseAttributes(root[0]);
      if (attrs.width && attrs.height) {
        return calculateByDimensions(attrs);
      }
      if (attrs.viewbox) {
        return calculateByViewbox(attrs, attrs.viewbox);
      }
    }
    throw new TypeError('Invalid SVG');
  }
};

var tga = {};

Object.defineProperty(tga, "__esModule", {
  value: true
});
tga.TGA = void 0;
const utils_1$2 = utils$1;
tga.TGA = {
  validate(input) {
    return (0, utils_1$2.readUInt16LE)(input, 0) === 0 && (0, utils_1$2.readUInt16LE)(input, 4) === 0;
  },
  calculate(input) {
    return {
      height: (0, utils_1$2.readUInt16LE)(input, 14),
      width: (0, utils_1$2.readUInt16LE)(input, 12)
    };
  }
};

var tiff = {};

Object.defineProperty(tiff, "__esModule", {
  value: true
});
tiff.TIFF = void 0;
// based on http://www.compix.com/fileformattif.htm
// TO-DO: support big-endian as well
const fs$1 = fs$3;
const utils_1$1 = utils$1;
// Read IFD (image-file-directory) into a buffer
function readIFD(input, filepath, isBigEndian) {
  const ifdOffset = (0, utils_1$1.readUInt)(input, 32, 4, isBigEndian);
  // read only till the end of the file
  let bufferSize = 1024;
  const fileSize = fs$1.statSync(filepath).size;
  if (ifdOffset + bufferSize > fileSize) {
    bufferSize = fileSize - ifdOffset - 10;
  }
  // populate the buffer
  const endBuffer = new Uint8Array(bufferSize);
  const descriptor = fs$1.openSync(filepath, 'r');
  fs$1.readSync(descriptor, endBuffer, 0, bufferSize, ifdOffset);
  fs$1.closeSync(descriptor);
  return endBuffer.slice(2);
}
// TIFF values seem to be messed up on Big-Endian, this helps
function readValue(input, isBigEndian) {
  const low = (0, utils_1$1.readUInt)(input, 16, 8, isBigEndian);
  const high = (0, utils_1$1.readUInt)(input, 16, 10, isBigEndian);
  return (high << 16) + low;
}
// move to the next tag
function nextTag(input) {
  if (input.length > 24) {
    return input.slice(12);
  }
}
// Extract IFD tags from TIFF metadata
function extractTags(input, isBigEndian) {
  const tags = {};
  let temp = input;
  while (temp && temp.length) {
    const code = (0, utils_1$1.readUInt)(temp, 16, 0, isBigEndian);
    const type = (0, utils_1$1.readUInt)(temp, 16, 2, isBigEndian);
    const length = (0, utils_1$1.readUInt)(temp, 32, 4, isBigEndian);
    // 0 means end of IFD
    if (code === 0) {
      break;
    } else {
      // 256 is width, 257 is height
      // if (code === 256 || code === 257) {
      if (length === 1 && (type === 3 || type === 4)) {
        tags[code] = readValue(temp, isBigEndian);
      }
      // move to the next tag
      temp = nextTag(temp);
    }
  }
  return tags;
}
// Test if the TIFF is Big Endian or Little Endian
function determineEndianness(input) {
  const signature = (0, utils_1$1.toUTF8String)(input, 0, 2);
  if ('II' === signature) {
    return 'LE';
  } else if ('MM' === signature) {
    return 'BE';
  }
}
const signatures = [
// '492049', // currently not supported
'49492a00',
// Little endian
'4d4d002a' // Big Endian
// '4d4d002a', // BigTIFF > 4GB. currently not supported
];
tiff.TIFF = {
  validate: input => signatures.includes((0, utils_1$1.toHexString)(input, 0, 4)),
  calculate(input, filepath) {
    if (!filepath) {
      throw new TypeError('Tiff doesn\'t support buffer');
    }
    // Determine BE/LE
    const isBigEndian = determineEndianness(input) === 'BE';
    // read the IFD
    const ifdBuffer = readIFD(input, filepath, isBigEndian);
    // extract the tags from the IFD
    const tags = extractTags(ifdBuffer, isBigEndian);
    const width = tags[256];
    const height = tags[257];
    if (!width || !height) {
      throw new TypeError('Invalid Tiff. Missing tags');
    }
    return {
      height,
      width
    };
  }
};

var webp = {};

Object.defineProperty(webp, "__esModule", {
  value: true
});
webp.WEBP = void 0;
const utils_1 = utils$1;
function calculateExtended(input) {
  return {
    height: 1 + (0, utils_1.readUInt24LE)(input, 7),
    width: 1 + (0, utils_1.readUInt24LE)(input, 4)
  };
}
function calculateLossless(input) {
  return {
    height: 1 + ((input[4] & 0xf) << 10 | input[3] << 2 | (input[2] & 0xc0) >> 6),
    width: 1 + ((input[2] & 0x3f) << 8 | input[1])
  };
}
function calculateLossy(input) {
  // `& 0x3fff` returns the last 14 bits
  // TO-DO: include webp scaling in the calculations
  return {
    height: (0, utils_1.readInt16LE)(input, 8) & 0x3fff,
    width: (0, utils_1.readInt16LE)(input, 6) & 0x3fff
  };
}
webp.WEBP = {
  validate(input) {
    const riffHeader = 'RIFF' === (0, utils_1.toUTF8String)(input, 0, 4);
    const webpHeader = 'WEBP' === (0, utils_1.toUTF8String)(input, 8, 12);
    const vp8Header = 'VP8' === (0, utils_1.toUTF8String)(input, 12, 15);
    return riffHeader && webpHeader && vp8Header;
  },
  calculate(input) {
    const chunkHeader = (0, utils_1.toUTF8String)(input, 12, 16);
    input = input.slice(20, 30);
    // Extended webp stream signature
    if (chunkHeader === 'VP8X') {
      const extendedHeader = input[0];
      const validStart = (extendedHeader & 0xc0) === 0;
      const validEnd = (extendedHeader & 0x01) === 0;
      if (validStart && validEnd) {
        return calculateExtended(input);
      } else {
        // TODO: breaking change
        throw new TypeError('Invalid WebP');
      }
    }
    // Lossless webp stream signature
    if (chunkHeader === 'VP8 ' && input[0] !== 0x2f) {
      return calculateLossy(input);
    }
    // Lossy webp stream signature
    const signature = (0, utils_1.toHexString)(input, 3, 6);
    if (chunkHeader === 'VP8L' && signature !== '9d012a') {
      return calculateLossless(input);
    }
    throw new TypeError('Invalid WebP');
  }
};

Object.defineProperty(types$1, "__esModule", {
  value: true
});
types$1.typeHandlers = void 0;
// load all available handlers explicitly for browserify support
const bmp_1 = bmp;
const cur_1 = cur;
const dds_1 = dds;
const gif_1 = gif;
const heif_1 = heif;
const icns_1 = icns;
const ico_1 = ico;
const j2c_1 = j2c;
const jp2_1 = jp2;
const jpg_1 = jpg;
const ktx_1 = ktx;
const png_1 = png;
const pnm_1 = pnm;
const psd_1 = psd;
const svg_1 = svg;
const tga_1 = tga;
const tiff_1 = tiff;
const webp_1 = webp;
types$1.typeHandlers = {
  bmp: bmp_1.BMP,
  cur: cur_1.CUR,
  dds: dds_1.DDS,
  gif: gif_1.GIF,
  heif: heif_1.HEIF,
  icns: icns_1.ICNS,
  ico: ico_1.ICO,
  j2c: j2c_1.J2C,
  jp2: jp2_1.JP2,
  jpg: jpg_1.JPG,
  ktx: ktx_1.KTX,
  png: png_1.PNG,
  pnm: pnm_1.PNM,
  psd: psd_1.PSD,
  svg: svg_1.SVG,
  tga: tga_1.TGA,
  tiff: tiff_1.TIFF,
  webp: webp_1.WEBP
};

var detector$1 = {};

Object.defineProperty(detector$1, "__esModule", {
  value: true
});
detector$1.detector = void 0;
const index_1 = types$1;
const keys = Object.keys(index_1.typeHandlers);
// This map helps avoid validating for every single image type
const firstBytes = {
  0x38: 'psd',
  0x42: 'bmp',
  0x44: 'dds',
  0x47: 'gif',
  0x49: 'tiff',
  0x4d: 'tiff',
  0x52: 'webp',
  0x69: 'icns',
  0x89: 'png',
  0xff: 'jpg'
};
function detector(input) {
  const byte = input[0];
  if (byte in firstBytes) {
    const type = firstBytes[byte];
    if (type && index_1.typeHandlers[type].validate(input)) {
      return type;
    }
  }
  const finder = key => index_1.typeHandlers[key].validate(input);
  return keys.find(finder);
}
detector$1.detector = detector;

(function (module, exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.types = exports.setConcurrency = exports.disableTypes = exports.disableFS = exports.imageSize = void 0;
	const fs = fs$3;
	const path = path$2;
	const queue_1 = queueExports;
	const index_1 = types$1;
	const detector_1 = detector$1;
	// Maximum input size, with a default of 512 kilobytes.
	// TO-DO: make this adaptive based on the initial signature of the image
	const MaxInputSize = 512 * 1024;
	// This queue is for async `fs` operations, to avoid reaching file-descriptor limits
	const queue = new queue_1.default({
	  concurrency: 100,
	  autostart: true
	});
	const globalOptions = {
	  disabledFS: false,
	  disabledTypes: []
	};
	/**
	 * Return size information based on an Uint8Array
	 *
	 * @param {Uint8Array} input
	 * @param {String} filepath
	 * @returns {Object}
	 */
	function lookup(input, filepath) {
	  // detect the file type.. don't rely on the extension
	  const type = (0, detector_1.detector)(input);
	  if (typeof type !== 'undefined') {
	    if (globalOptions.disabledTypes.indexOf(type) > -1) {
	      throw new TypeError('disabled file type: ' + type);
	    }
	    // find an appropriate handler for this file type
	    if (type in index_1.typeHandlers) {
	      const size = index_1.typeHandlers[type].calculate(input, filepath);
	      if (size !== undefined) {
	        size.type = size.type ?? type;
	        return size;
	      }
	    }
	  }
	  // throw up, if we don't understand the file
	  throw new TypeError('unsupported file type: ' + type + ' (file: ' + filepath + ')');
	}
	/**
	 * Reads a file into an Uint8Array.
	 * @param {String} filepath
	 * @returns {Promise<Uint8Array>}
	 */
	async function readFileAsync(filepath) {
	  const handle = await fs.promises.open(filepath, 'r');
	  try {
	    const {
	      size
	    } = await handle.stat();
	    if (size <= 0) {
	      throw new Error('Empty file');
	    }
	    const inputSize = Math.min(size, MaxInputSize);
	    const input = new Uint8Array(inputSize);
	    await handle.read(input, 0, inputSize, 0);
	    return input;
	  } finally {
	    await handle.close();
	  }
	}
	/**
	 * Synchronously reads a file into an Uint8Array, blocking the nodejs process.
	 *
	 * @param {String} filepath
	 * @returns {Uint8Array}
	 */
	function readFileSync(filepath) {
	  // read from the file, synchronously
	  const descriptor = fs.openSync(filepath, 'r');
	  try {
	    const {
	      size
	    } = fs.fstatSync(descriptor);
	    if (size <= 0) {
	      throw new Error('Empty file');
	    }
	    const inputSize = Math.min(size, MaxInputSize);
	    const input = new Uint8Array(inputSize);
	    fs.readSync(descriptor, input, 0, inputSize, 0);
	    return input;
	  } finally {
	    fs.closeSync(descriptor);
	  }
	}
	// eslint-disable-next-line @typescript-eslint/no-use-before-define
	module.exports = exports = imageSize; // backwards compatibility
	exports.default = imageSize;
	/**
	 * @param {Uint8Array|string} input - Uint8Array or relative/absolute path of the image file
	 * @param {Function=} [callback] - optional function for async detection
	 */
	function imageSize(input, callback) {
	  // Handle Uint8Array input
	  if (input instanceof Uint8Array) {
	    return lookup(input);
	  }
	  // input should be a string at this point
	  if (typeof input !== 'string' || globalOptions.disabledFS) {
	    throw new TypeError('invalid invocation. input should be a Uint8Array');
	  }
	  // resolve the file path
	  const filepath = path.resolve(input);
	  if (typeof callback === 'function') {
	    queue.push(() => readFileAsync(filepath).then(input => process.nextTick(callback, null, lookup(input, filepath))).catch(callback));
	  } else {
	    const input = readFileSync(filepath);
	    return lookup(input, filepath);
	  }
	}
	exports.imageSize = imageSize;
	const disableFS = v => {
	  globalOptions.disabledFS = v;
	};
	exports.disableFS = disableFS;
	const disableTypes = types => {
	  globalOptions.disabledTypes = types;
	};
	exports.disableTypes = disableTypes;
	const setConcurrency = c => {
	  queue.concurrency = c;
	};
	exports.setConcurrency = setConcurrency;
	exports.types = Object.keys(index_1.typeHandlers); 
} (dist, dist.exports));

var distExports = dist.exports;
const imageSize = /*@__PURE__*/getDefaultExportFromCjs(distExports);

let PlatformType = /* @__PURE__ */ function(PlatformType2) {
  PlatformType2[PlatformType2["KUNKNOWN"] = 0] = "KUNKNOWN";
  PlatformType2[PlatformType2["KANDROID"] = 1] = "KANDROID";
  PlatformType2[PlatformType2["KIOS"] = 2] = "KIOS";
  PlatformType2[PlatformType2["KWINDOWS"] = 3] = "KWINDOWS";
  PlatformType2[PlatformType2["KMAC"] = 4] = "KMAC";
  return PlatformType2;
}({});
let VendorType = /* @__PURE__ */ function(VendorType2) {
  VendorType2[VendorType2["KNOSETONIOS"] = 0] = "KNOSETONIOS";
  VendorType2[VendorType2["KSUPPORTGOOGLEPUSH"] = 99] = "KSUPPORTGOOGLEPUSH";
  VendorType2[VendorType2["KSUPPORTHMS"] = 3] = "KSUPPORTHMS";
  VendorType2[VendorType2["KSUPPORTOPPOPUSH"] = 4] = "KSUPPORTOPPOPUSH";
  VendorType2[VendorType2["KSUPPORTTPNS"] = 2] = "KSUPPORTTPNS";
  VendorType2[VendorType2["KSUPPORTVIVOPUSH"] = 5] = "KSUPPORTVIVOPUSH";
  VendorType2[VendorType2["KUNSUPPORTANDROIDPUSH"] = 1] = "KUNSUPPORTANDROIDPUSH";
  return VendorType2;
}({});
const sessionConfig = {};
async function genSessionConfig(selfUin, selfUid, account_path) {
  const downloadPath = path__default.join(account_path, "NapCat", "temp");
  fs__default.mkdirSync(downloadPath, {
    recursive: true
  });
  let guid = await getMachineId();
  const config = {
    selfUin,
    selfUid,
    desktopPathConfig: {
      account_path
      // 可以通过NodeQQNTWrapperUtil().getNTUserDataInfoConfig()获取
    },
    clientVer: getFullQQVesion(),
    // 9.9.8-22355
    a2: "",
    d2: "",
    d2Key: "",
    machineId: "",
    platform: PlatformType.KWINDOWS,
    // 3是Windows?
    platVer: systemVersion,
    // 系统版本号, 应该可以固定
    appid: QQVersionAppid,
    rdeliveryConfig: {
      appKey: "",
      systemId: 0,
      appId: "",
      logicEnvironment: "",
      platform: PlatformType.KWINDOWS,
      language: "",
      sdkVersion: "",
      userId: "",
      appVersion: "",
      osVersion: "",
      bundleId: "",
      serverUrl: "",
      fixedAfterHitKeys: [""]
    },
    defaultFileDownloadPath: downloadPath,
    deviceInfo: {
      guid,
      buildVer: getFullQQVesion(),
      localId: 2052,
      devName: hostname,
      devType: systemName,
      vendorName: "",
      osVer: systemVersion,
      vendorOsName: systemName,
      setMute: false,
      vendorType: VendorType.KNOSETONIOS
    },
    deviceConfig: '{"appearance":{"isSplitViewMode":true},"msg":{}}'
  };
  Object.assign(sessionConfig, config);
  return config;
}

class RequestUtil {
  // 适用于获取服务器下发cookies时获取，仅GET
  static async HttpsGetCookies(url) {
    const client = url.startsWith("https") ? https$1 : http$1;
    return new Promise((resolve, reject) => {
      const req = client.get(url, (res) => {
        let cookies = {};
        const handleRedirect = (res2) => {
          if (res2.statusCode === 301 || res2.statusCode === 302) {
            if (res2.headers.location) {
              const redirectUrl = new URL(res2.headers.location, url);
              RequestUtil.HttpsGetCookies(redirectUrl.href).then((redirectCookies) => {
                cookies = {
                  ...cookies,
                  ...redirectCookies
                };
                resolve(cookies);
              }).catch((err) => {
                reject(err);
              });
            } else {
              resolve(cookies);
            }
          } else {
            resolve(cookies);
          }
        };
        res.on("data", () => {
        });
        res.on("end", () => {
          handleRedirect(res);
        });
        if (res.headers["set-cookie"]) {
          res.headers["set-cookie"].forEach((cookie) => {
            const parts = cookie.split(";")[0].split("=");
            const key = parts[0];
            const value = parts[1];
            if (key && value && key.length > 0 && value.length > 0) {
              cookies[key] = value;
            }
          });
        }
      });
      req.on("error", (error) => {
        reject(error);
      });
    });
  }
  // 请求和回复都是JSON data传原始内容 自动编码json
  static async HttpGetJson(url, method = "GET", data, headers = {}, isJsonRet = true, isArgJson = true) {
    const option = new URL(url);
    const protocol = url.startsWith("https://") ? https$1 : http$1;
    const options = {
      hostname: option.hostname,
      port: option.port,
      path: option.href,
      method,
      headers
    };
    return new Promise((resolve, reject) => {
      const req = protocol.request(options, (res) => {
        let responseBody = "";
        res.on("data", (chunk) => {
          responseBody += chunk.toString();
        });
        res.on("end", () => {
          try {
            if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
              if (isJsonRet) {
                const responseJson = JSON.parse(responseBody);
                resolve(responseJson);
              } else {
                resolve(responseBody);
              }
            } else {
              reject(new Error(`Unexpected status code: ${res.statusCode}`));
            }
          } catch (parseError) {
            reject(parseError);
          }
        });
      });
      req.on("error", (error) => {
        reject(error);
      });
      if (method === "POST" || method === "PUT" || method === "PATCH") {
        if (isArgJson) {
          req.write(JSON.stringify(data));
        } else {
          req.write(data);
        }
      }
      req.end();
    });
  }
  // 请求返回都是原始内容
  static async HttpGetText(url, method = "GET", data, headers = {}) {
    return this.HttpGetJson(url, method, data, headers, false, false);
  }
  static async createFormData(boundary, filePath) {
    let type = "image/png";
    if (filePath.endsWith(".jpg")) {
      type = "image/jpeg";
    }
    const formDataParts = [`------${boundary}\r
`, `Content-Disposition: form-data; name="share_image"; filename="${filePath}"\r
`, "Content-Type: " + type + "\r\n\r\n"];
    const fileContent = readFileSync(filePath);
    const footer = `\r
------${boundary}--`;
    return Buffer.concat([Buffer.from(formDataParts.join(""), "utf8"), fileContent, Buffer.from(footer, "utf8")]);
  }
  static async uploadImageForOpenPlatform(filePath) {
    return new Promise(async (resolve, reject) => {
      try {
        const cookies = Object.entries(await NTQQUserApi.getCookies("connect.qq.com")).map(([key, value]) => `${key}=${value}`).join("; ");
        const options = {
          hostname: "cgi.connect.qq.com",
          port: 443,
          path: "/qqconnectopen/upload_share_image",
          method: "POST",
          headers: {
            "Referer": "https://cgi.connect.qq.com",
            "Cookie": cookies,
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"
          }
        };
        const req = https$1.request(options, async (res) => {
          let responseBody = "";
          res.on("data", (chunk) => {
            responseBody += chunk.toString();
          });
          res.on("end", () => {
            try {
              if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                const responseJson = JSON.parse(responseBody);
                resolve(responseJson.result.url);
              } else {
                reject(new Error(`Unexpected status code: ${res.statusCode}`));
              }
            } catch (parseError) {
              reject(parseError);
            }
          });
        });
        req.on("error", (error) => {
          reject(error);
          console.error("Error during upload:", error);
        });
        const body = await RequestUtil.createFormData("WebKitFormBoundary7MA4YWxkTrZu0gW", filePath);
        req.write(body);
        req.end();
        return;
      } catch (error) {
        reject(error);
      }
      return void 0;
    });
  }
}

function _defineProperty$1J(e, r, t) {
  return (r = _toPropertyKey$1J(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1J(t) {
  var i = _toPrimitive$1J(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1J(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class RkeyManager {
  constructor(serverUrl) {
    _defineProperty$1J(this, "serverUrl", "");
    _defineProperty$1J(this, "rkeyData", {
      group_rkey: "",
      private_rkey: "",
      expired_time: 0
    });
    this.serverUrl = serverUrl;
  }
  async getRkey() {
    if (this.isExpired()) {
      try {
        await this.refreshRkey();
      } catch (e) {
        logError("获取rkey失败", e);
      }
    }
    return this.rkeyData;
  }
  isExpired() {
    const now = (/* @__PURE__ */ new Date()).getTime() / 1e3;
    return now > this.rkeyData.expired_time;
  }
  async refreshRkey() {
    this.rkeyData = await RequestUtil.HttpGetJson(this.serverUrl, "GET");
  }
}
const rkeyManager = new RkeyManager("http://napcat-sign.wumiao.wang:2082/rkey");

function _defineProperty$1I(e, r, t) {
  return (r = _toPropertyKey$1I(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1I(t) {
  var i = _toPrimitive$1I(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1I(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class NTEventWrapper {
  //tasks ListenerMainName -> ListenerSubName-> uuid -> {timeout,createtime,func}
  constructor() {
    _defineProperty$1I(this, "ListenerMap", void 0);
    _defineProperty$1I(this, "WrapperSession", void 0);
    _defineProperty$1I(this, "ListenerManger", /* @__PURE__ */ new Map());
    _defineProperty$1I(this, "EventTask", /* @__PURE__ */ new Map());
  }
  createProxyDispatch(ListenerMainName) {
    const current = this;
    return new Proxy({}, {
      get(target, prop, receiver) {
        if (typeof target[prop] === "undefined") {
          return (...args) => {
            current.DispatcherListener.apply(current, [ListenerMainName, prop, ...args]).then();
          };
        }
        return Reflect.get(target, prop, receiver);
      }
    });
  }
  init({
    ListenerMap,
    WrapperSession
  }) {
    this.ListenerMap = ListenerMap;
    this.WrapperSession = WrapperSession;
  }
  CreatEventFunction(eventName) {
    const eventNameArr = eventName.split("/");
    if (eventNameArr.length > 1) {
      const serviceName = "get" + eventNameArr[0].replace("NodeIKernel", "");
      const eventName2 = eventNameArr[1];
      const services = this.WrapperSession[serviceName]();
      let event = services[eventName2];
      event = event.bind(services);
      if (event) {
        return event;
      }
      return void 0;
    }
  }
  CreatListenerFunction(listenerMainName, uniqueCode = "") {
    const ListenerType = this.ListenerMap[listenerMainName];
    let Listener = this.ListenerManger.get(listenerMainName + uniqueCode);
    if (!Listener && ListenerType) {
      Listener = new ListenerType(this.createProxyDispatch(listenerMainName));
      const ServiceSubName = listenerMainName.match(/^NodeIKernel(.*?)Listener$/)[1];
      const Service = "NodeIKernel" + ServiceSubName + "Service/addKernel" + ServiceSubName + "Listener";
      const addfunc = this.CreatEventFunction(Service);
      addfunc(Listener);
      this.ListenerManger.set(listenerMainName + uniqueCode, Listener);
    }
    return Listener;
  }
  //统一回调清理事件
  async DispatcherListener(ListenerMainName, ListenerSubName, ...args) {
    this.EventTask.get(ListenerMainName)?.get(ListenerSubName)?.forEach((task, uuid) => {
      if (task.createtime + task.timeout < Date.now()) {
        this.EventTask.get(ListenerMainName)?.get(ListenerSubName)?.delete(uuid);
        return;
      }
      if (task.checker && task.checker(...args)) {
        task.func(...args);
      }
    });
  }
  async CallNoListenerEvent(EventName = "", timeout = 3e3, ...args) {
    return new Promise(async (resolve, reject) => {
      const EventFunc = this.CreatEventFunction(EventName);
      let complete = false;
      setTimeout(() => {
        if (!complete) {
          reject(new Error("NTEvent EventName:" + EventName + " timeout"));
        }
      }, timeout);
      const retData = await EventFunc(...args);
      complete = true;
      resolve(retData);
    });
  }
  async RegisterListen(ListenerName = "", waitTimes = 1, timeout = 5e3, checker) {
    return new Promise((resolve, reject) => {
      const ListenerNameList = ListenerName.split("/");
      const ListenerMainName = ListenerNameList[0];
      const ListenerSubName = ListenerNameList[1];
      const id = randomUUID();
      let complete = 0;
      let retData = void 0;
      const databack = () => {
        if (complete == 0) {
          reject(new Error(" ListenerName:" + ListenerName + " timeout"));
        } else {
          resolve(retData);
        }
      };
      const Timeouter = setTimeout(databack, timeout);
      const eventCallbak = {
        timeout,
        createtime: Date.now(),
        checker,
        func: (...args) => {
          complete++;
          retData = args;
          if (complete >= waitTimes) {
            clearTimeout(Timeouter);
            databack();
          }
        }
      };
      if (!this.EventTask.get(ListenerMainName)) {
        this.EventTask.set(ListenerMainName, /* @__PURE__ */ new Map());
      }
      if (!this.EventTask.get(ListenerMainName)?.get(ListenerSubName)) {
        this.EventTask.get(ListenerMainName)?.set(ListenerSubName, /* @__PURE__ */ new Map());
      }
      this.EventTask.get(ListenerMainName)?.get(ListenerSubName)?.set(id, eventCallbak);
      this.CreatListenerFunction(ListenerMainName);
    });
  }
  async CallNormalEvent(EventName = "", ListenerName = "", waitTimes = 1, timeout = 3e3, checker, ...args) {
    return new Promise(async (resolve, reject) => {
      const id = randomUUID();
      let complete = 0;
      let retData = void 0;
      let retEvent = {};
      const databack = () => {
        if (complete == 0) {
          reject(new Error("Timeout: NTEvent EventName:" + EventName + " ListenerName:" + ListenerName + " EventRet:\n" + JSON.stringify(retEvent, null, 4) + "\n"));
        } else {
          resolve([retEvent, ...retData]);
        }
      };
      const ListenerNameList = ListenerName.split("/");
      const ListenerMainName = ListenerNameList[0];
      const ListenerSubName = ListenerNameList[1];
      const Timeouter = setTimeout(databack, timeout);
      const eventCallbak = {
        timeout,
        createtime: Date.now(),
        checker,
        func: (...args2) => {
          complete++;
          retData = args2;
          if (complete >= waitTimes) {
            clearTimeout(Timeouter);
            databack();
          }
        }
      };
      if (!this.EventTask.get(ListenerMainName)) {
        this.EventTask.set(ListenerMainName, /* @__PURE__ */ new Map());
      }
      if (!this.EventTask.get(ListenerMainName)?.get(ListenerSubName)) {
        this.EventTask.get(ListenerMainName)?.set(ListenerSubName, /* @__PURE__ */ new Map());
      }
      this.EventTask.get(ListenerMainName)?.get(ListenerSubName)?.set(id, eventCallbak);
      this.CreatListenerFunction(ListenerMainName);
      const EventFunc = this.CreatEventFunction(EventName);
      retEvent = await EventFunc(...args);
    });
  }
}
const NTEventDispatch = new NTEventWrapper();

class NTQQFileApi {
  static async getFileType(filePath) {
    return fileTypeFromFile(filePath);
  }
  static async copyFile(filePath, destPath) {
    await napCatCore.util.copyFile(filePath, destPath);
  }
  static async getFileSize(filePath) {
    return await napCatCore.util.getFileSize(filePath);
  }
  static async getVideoUrl(peer, msgId, elementId) {
    return (await napCatCore.session.getRichMediaService().getVideoPlayUrlV2(peer, msgId, elementId, 0, {
      downSourceType: 1,
      triggerType: 1
    })).urlResult.domainUrl;
  }
  // 上传文件到QQ的文件夹
  static async uploadFile(filePath, elementType = ElementType.PIC, elementSubType = 0) {
    const fileMd5 = await calculateFileMD5(filePath);
    let ext = (await NTQQFileApi.getFileType(filePath))?.ext || "";
    if (ext) {
      ext = "." + ext;
    }
    let fileName = `${path$2.basename(filePath)}`;
    if (fileName.indexOf(".") === -1) {
      fileName += ext;
    }
    const mediaPath = napCatCore.session.getMsgService().getRichMediaFilePathForGuild({
      md5HexStr: fileMd5,
      fileName,
      elementType,
      elementSubType,
      thumbSize: 0,
      needCreate: true,
      downloadType: 1,
      file_uuid: ""
    });
    await NTQQFileApi.copyFile(filePath, mediaPath);
    const fileSize = await NTQQFileApi.getFileSize(filePath);
    return {
      md5: fileMd5,
      fileName,
      path: mediaPath,
      fileSize,
      ext
    };
  }
  static async downloadMediaByUuid() {
  }
  static async downloadMedia(msgId, chatType, peerUid, elementId, thumbPath, sourcePath, timeout = 1e3 * 60 * 2, force = false) {
    if (sourcePath && fs$3.existsSync(sourcePath)) {
      if (force) {
        try {
          await fsPromise.unlink(sourcePath);
        } catch (e) {
        }
      } else {
        return sourcePath;
      }
    }
    let data = await NTEventDispatch.CallNormalEvent("NodeIKernelMsgService/downloadRichMedia", "NodeIKernelMsgListener/onRichMediaDownloadComplete", 1, timeout, (arg) => {
      if (arg.msgId === msgId) {
        return true;
      }
      return false;
    }, {
      fileModelId: "0",
      downloadSourceType: 0,
      triggerType: 1,
      msgId,
      chatType,
      peerUid,
      elementId,
      thumbSize: 0,
      downloadType: 1,
      filePath: thumbPath
    });
    let filePath = data[1].filePath;
    if (filePath.startsWith("\\")) {
      const downloadPath = sessionConfig.defaultFileDownloadPath;
      filePath = path$2.join(downloadPath, filePath);
    }
    return filePath;
  }
  static async getImageSize(filePath) {
    return new Promise((resolve, reject) => {
      imageSize(filePath, (err, dimensions) => {
        if (err) {
          reject(err);
        } else {
          resolve(dimensions);
        }
      });
    });
  }
  static async addFileCache(peer, msgId, msgSeq, senderUid, elemId, elemType, fileSize, fileName) {
    let GroupData;
    let BuddyData;
    if (peer.chatType === ChatType.group) {
      GroupData = [{
        groupCode: peer.peerUid,
        isConf: false,
        hasModifyConfGroupFace: true,
        hasModifyConfGroupName: true,
        groupName: "NapCat.Cached",
        remark: "NapCat.Cached"
      }];
    } else if (peer.chatType === ChatType.friend) {
      BuddyData = [{
        category_name: "NapCat.Cached",
        peerUid: peer.peerUid,
        peerUin: peer.peerUid,
        remark: "NapCat.Cached"
      }];
    } else {
      return void 0;
    }
    return napCatCore.session.getSearchService().addSearchHistory({
      type: 4,
      contactList: [],
      id: -1,
      groupInfos: [],
      msgs: [],
      fileInfos: [{
        chatType: peer.chatType,
        buddyChatInfo: BuddyData || [],
        discussChatInfo: [],
        groupChatInfo: GroupData || [],
        dataLineChatInfo: [],
        tmpChatInfo: [],
        msgId,
        msgSeq,
        msgTime: Math.floor(Date.now() / 1e3).toString(),
        senderUid,
        senderNick: "NapCat.Cached",
        senderRemark: "NapCat.Cached",
        senderCard: "NapCat.Cached",
        elemId,
        elemType,
        fileSize,
        filePath: "",
        fileName,
        hits: [{
          start: 12,
          end: 14
        }]
      }]
    });
  }
  static async searchfile(keys) {
    const Event = await NTEventDispatch.CreatEventFunction("NodeIKernelSearchService/searchFileWithKeywords");
    let id = "";
    const Listener = NTEventDispatch.RegisterListen("NodeIKernelSearchListener/onSearchFileKeywordsResult", 1, 2e4, (params) => {
      if (id !== "" && params.searchId == id) {
        return true;
      }
      return false;
    });
    id = await Event(keys, 12);
    let [ret] = await Listener;
    return ret;
  }
  static async getImageUrl(element) {
    if (!element) {
      return "";
    }
    const url = element.originImageUrl;
    const md5HexStr = element.md5HexStr;
    const fileMd5 = element.md5HexStr;
    element.fileUuid;
    if (url) {
      let UrlParse = new URL(IMAGE_HTTP_HOST + url);
      let imageAppid = UrlParse.searchParams.get("appid");
      let isNewPic = imageAppid && ["1406", "1407"].includes(imageAppid);
      if (isNewPic) {
        let UrlRkey = UrlParse.searchParams.get("rkey");
        if (UrlRkey) {
          return IMAGE_HTTP_HOST_NT + url;
        }
        const rkeyData = await rkeyManager.getRkey();
        UrlRkey = imageAppid === "1406" ? rkeyData.private_rkey : rkeyData.group_rkey;
        return IMAGE_HTTP_HOST_NT + url + `${UrlRkey}`;
      } else {
        return IMAGE_HTTP_HOST + url;
      }
    } else if (fileMd5 || md5HexStr) {
      return `${IMAGE_HTTP_HOST}/gchatpic_new/0/0-0-${(fileMd5 || md5HexStr).toUpperCase()}/0`;
    }
    logDebug("图片url获取失败", element);
    return "";
  }
}

function _defineProperty$1H(e, r, t) {
  return (r = _toPropertyKey$1H(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1H(t) {
  var i = _toPrimitive$1H(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1H(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class LimitedHashTable {
  constructor(maxSize) {
    _defineProperty$1H(this, "keyToValue", /* @__PURE__ */ new Map());
    _defineProperty$1H(this, "valueToKey", /* @__PURE__ */ new Map());
    _defineProperty$1H(this, "maxSize", void 0);
    this.maxSize = maxSize;
  }
  resize(count) {
    this.maxSize = count;
  }
  set(key, value) {
    this.keyToValue.set(key, value);
    this.valueToKey.set(value, key);
    while (this.keyToValue.size !== this.valueToKey.size) {
      console.log("keyToValue.size !== valueToKey.size Error Atom");
      this.keyToValue.clear();
      this.valueToKey.clear();
    }
    while (this.keyToValue.size > this.maxSize || this.valueToKey.size > this.maxSize) {
      const oldestKey = this.keyToValue.keys().next().value;
      this.valueToKey.delete(this.keyToValue.get(oldestKey));
      this.keyToValue.delete(oldestKey);
    }
  }
  getValue(key) {
    return this.keyToValue.get(key);
  }
  getKey(value) {
    return this.valueToKey.get(value);
  }
  deleteByValue(value) {
    const key = this.valueToKey.get(value);
    if (key !== void 0) {
      this.keyToValue.delete(key);
      this.valueToKey.delete(value);
    }
  }
  deleteByKey(key) {
    const value = this.keyToValue.get(key);
    if (value !== void 0) {
      this.keyToValue.delete(key);
      this.valueToKey.delete(value);
    }
  }
  getKeyList() {
    return Array.from(this.keyToValue.keys());
  }
  //获取最近刚写入的几个值
  getHeads(size) {
    const keyList = this.getKeyList();
    if (keyList.length === 0) {
      return void 0;
    }
    const result = [];
    const listSize = Math.min(size, keyList.length);
    for (let i = 0; i < listSize; i++) {
      const key = keyList[listSize - i];
      result.push({
        key,
        value: this.keyToValue.get(key)
      });
    }
    return result;
  }
}
class MessageUniqueWrapper {
  constructor(maxMap = 1e3) {
    _defineProperty$1H(this, "msgDataMap", void 0);
    _defineProperty$1H(this, "msgIdMap", void 0);
    this.msgIdMap = new LimitedHashTable(maxMap);
    this.msgDataMap = new LimitedHashTable(maxMap);
  }
  getRecentMsgIds(Peer, size) {
    const heads = this.msgIdMap.getHeads(size);
    if (!heads) {
      return [];
    }
    const data = heads.map((t) => MessageUnique.getMsgIdAndPeerByShortId(t.value));
    const ret = data.filter((t) => t?.Peer.chatType === Peer.chatType && t?.Peer.peerUid === Peer.peerUid);
    return ret.map((t) => t?.MsgId).filter((t) => t !== void 0);
  }
  createMsg(peer, msgId) {
    const key = `${msgId}|${peer.chatType}|${peer.peerUid}`;
    const hash = crypto.createHash("md5").update(key).digest();
    hash[0] &= 127;
    const shortId = hash.readInt32BE(0);
    this.msgIdMap.set(msgId, shortId);
    this.msgDataMap.set(key, shortId);
    return shortId;
  }
  getMsgIdAndPeerByShortId(shortId) {
    const data = this.msgDataMap.getKey(shortId);
    if (data) {
      const [msgId, chatTypeStr, peerUid] = data.split("|");
      const peer = {
        chatType: parseInt(chatTypeStr),
        peerUid,
        guildId: ""
      };
      return {
        MsgId: msgId,
        Peer: peer
      };
    }
    return void 0;
  }
  getShortIdByMsgId(msgId) {
    return this.msgIdMap.getValue(msgId);
  }
  getPeerByMsgId(msgId) {
    const shortId = this.msgIdMap.getValue(msgId);
    if (!shortId) return void 0;
    return this.getMsgIdAndPeerByShortId(shortId);
  }
  resize(maxSize) {
    this.msgIdMap.resize(maxSize);
    this.msgDataMap.resize(maxSize);
  }
}
const MessageUnique = new MessageUniqueWrapper();

var _dec$3, _class$3;
function _applyDecoratedDescriptor$3(i, e, r, n, l) {
  var a = {};
  return Object.keys(n).forEach(function(i2) {
    a[i2] = n[i2];
  }), a.enumerable = !!a.enumerable, a.configurable = !!a.configurable, ("value" in a || a.initializer) && (a.writable = true), a = r.slice().reverse().reduce(function(r2, n2) {
    return n2(i, e, r2) || r2;
  }, a), l && void 0 !== a.initializer && (a.value = a.initializer ? a.initializer.call(l) : void 0, a.initializer = void 0), void 0 === a.initializer ? (Object.defineProperty(i, e, a), null) : a;
}
let NTQQFriendApi = (_dec$3 = CacheClassFuncAsyncExtend(3600 * 1e3, "getBuddyIdMap", () => true), _class$3 = class NTQQFriendApi2 {
  static async getBuddyV2(refresh = false) {
    let uids = [];
    const buddyService = napCatCore.session.getBuddyService();
    const buddyListV2 = refresh ? await buddyService.getBuddyListV2("0", BuddyListReqType.KNOMAL) : await buddyService.getBuddyListV2("0", BuddyListReqType.KNOMAL);
    uids.push(...buddyListV2.data.flatMap((item) => item.buddyUids));
    const data = await NTEventDispatch.CallNoListenerEvent("NodeIKernelProfileService/getCoreAndBaseInfo", 5e3, "nodeStore", uids);
    return Array.from(data.values());
  }
  static async getBuddyIdMapCache(refresh = false) {
    return await NTQQFriendApi2.getBuddyIdMap(refresh);
  }
  static async getBuddyIdMap(refresh = false) {
    let uids = [];
    let retMap = new LimitedHashTable(5e3);
    const buddyService = napCatCore.session.getBuddyService();
    const buddyListV2 = refresh ? await buddyService.getBuddyListV2("0", BuddyListReqType.KNOMAL) : await buddyService.getBuddyListV2("0", BuddyListReqType.KNOMAL);
    uids.push(...buddyListV2.data.flatMap((item) => item.buddyUids));
    const data = await NTEventDispatch.CallNoListenerEvent("NodeIKernelProfileService/getCoreAndBaseInfo", 5e3, "nodeStore", uids);
    data.forEach((value, key) => {
      retMap.set(value.uin, value.uid);
    });
    return retMap;
  }
  static async getBuddyV2ExWithCate(refresh = false) {
    let uids = [];
    let categoryMap = /* @__PURE__ */ new Map();
    const buddyService = napCatCore.session.getBuddyService();
    const buddyListV2 = refresh ? (await buddyService.getBuddyListV2("0", BuddyListReqType.KNOMAL)).data : (await buddyService.getBuddyListV2("0", BuddyListReqType.KNOMAL)).data;
    uids.push(...buddyListV2.flatMap((item) => {
      item.buddyUids.forEach((uid) => {
        categoryMap.set(uid, {
          categoryId: item.categoryId,
          categroyName: item.categroyName
        });
      });
      return item.buddyUids;
    }));
    const data = await NTEventDispatch.CallNoListenerEvent("NodeIKernelProfileService/getCoreAndBaseInfo", 5e3, "nodeStore", uids);
    return Array.from(data).map(([key, value]) => {
      const category = categoryMap.get(key);
      return category ? {
        ...value,
        categoryId: category.categoryId,
        categroyName: category.categroyName
      } : value;
    });
  }
  static async isBuddy(uid) {
    return napCatCore.session.getBuddyService().isBuddy(uid);
  }
  /**
   * @deprecated
   * @param forced 
   * @returns 
   */
  static async getFriends(forced = false) {
    let [_retData, _BuddyArg] = await NTEventDispatch.CallNormalEvent("NodeIKernelBuddyService/getBuddyList", "NodeIKernelBuddyListener/onBuddyListChange", 1, 5e3, () => true, forced);
    const friends = [];
    for (const categoryItem of _BuddyArg) {
      for (const friend of categoryItem.buddyList) {
        friends.push(friend);
      }
    }
    return friends;
  }
  static async handleFriendRequest(flag, accept) {
    let data = flag.split("|");
    if (data.length < 2) {
      return;
    }
    let friendUid = data[0];
    let reqTime = data[1];
    napCatCore.session.getBuddyService()?.approvalFriendRequest({
      friendUid,
      reqTime,
      accept
    });
  }
}, _applyDecoratedDescriptor$3(_class$3, "getBuddyIdMapCache", [_dec$3], Object.getOwnPropertyDescriptor(_class$3, "getBuddyIdMapCache"), _class$3), _class$3);

const selfInfo = {
  uid: "",
  uin: "",
  nick: "",
  online: true
};
const groups = /* @__PURE__ */ new Map();
function deleteGroup(groupQQ) {
  groups.delete(groupQQ);
  groupMembers.delete(groupQQ);
}
const groupMembers = /* @__PURE__ */ new Map();
const friends = /* @__PURE__ */ new Map();
async function getGroup(qq) {
  let group = groups.get(qq.toString());
  if (!group) {
    try {
      const _groups = await NTQQGroupApi.getGroups();
      if (_groups.length) {
        _groups.forEach((g) => {
          groups.set(g.groupCode, g);
        });
      }
    } catch (e) {
      return void 0;
    }
  }
  group = groups.get(qq.toString());
  return group;
}
async function getGroupMember(groupQQ, memberUinOrUid) {
  groupQQ = groupQQ.toString();
  memberUinOrUid = memberUinOrUid.toString();
  let members = groupMembers.get(groupQQ);
  if (!members) {
    try {
      members = await NTQQGroupApi.getGroupMembers(groupQQ);
      groupMembers.set(groupQQ, members);
    } catch (e) {
      return null;
    }
  }
  const getMember = () => {
    let member2 = void 0;
    if (isNumeric(memberUinOrUid)) {
      member2 = Array.from(members.values()).find((member3) => member3.uin === memberUinOrUid);
    } else {
      member2 = members.get(memberUinOrUid);
    }
    return member2;
  };
  let member = getMember();
  if (!member) {
    members = await NTQQGroupApi.getGroupMembers(groupQQ);
    member = getMember();
  }
  return member;
}
const stat = {
  packet_received: 0,
  packet_sent: 0,
  message_received: 0,
  message_sent: 0,
  last_message_time: 0,
  // 以下字段无用, 全部为0
  disconnect_times: 0,
  lost_times: 0,
  packet_lost: 0
};

var _dec$2, _class$2;
function _applyDecoratedDescriptor$2(i, e, r, n, l) {
  var a = {};
  return Object.keys(n).forEach(function(i2) {
    a[i2] = n[i2];
  }), a.enumerable = !!a.enumerable, a.configurable = !!a.configurable, ("value" in a || a.initializer) && (a.writable = true), a = r.slice().reverse().reduce(function(r2, n2) {
    return n2(i, e, r2) || r2;
  }, a), l && void 0 !== a.initializer && (a.value = a.initializer ? a.initializer.call(l) : void 0, a.initializer = void 0), void 0 === a.initializer ? (Object.defineProperty(i, e, a), null) : a;
}
let NTQQGroupApi = (_dec$2 = CacheClassFuncAsyncExtend(3600 * 1e3, "LastestSendTime", () => true), _class$2 = class NTQQGroupApi2 {
  static async setGroupAvatar(gc, filePath) {
    return napCatCore.session.getGroupService().setHeader(gc, filePath);
  }
  static async getGroups(forced = false) {
    let [_retData, _updateType, groupList] = await NTEventDispatch.CallNormalEvent("NodeIKernelGroupService/getGroupList", "NodeIKernelGroupListener/onGroupListUpdate", 1, 5e3, (updateType) => true, forced);
    return groupList;
  }
  static async getGroupMemberLastestSendTimeCache(GroupCode) {
    return NTQQGroupApi2.getGroupMemberLastestSendTime(GroupCode);
  }
  /**
   * 通过QQ自带数据库获取群成员最后发言时间(仅返回有效数据 且消耗延迟大 需要进行缓存)
   * @param GroupCode 群号
   * @returns Map<string, string> key: uin value: sendTime
   * @example
   * let ret = await NTQQGroupApi.getGroupMemberLastestSendTime('123456');
   * for (let [uin, sendTime] of ret) {
   *  console.log(uin, sendTime);
   * }
  */
  static async getGroupMemberLastestSendTime(GroupCode) {
    async function getdata(uid) {
      let NTRet = await NTQQGroupApi2.getLastestMsgByUids(GroupCode, [uid]);
      if (NTRet.result != 0 && NTRet.msgList.length < 1) {
        return void 0;
      }
      return {
        sendUin: NTRet.msgList[0].senderUin,
        sendTime: NTRet.msgList[0].msgTime
      };
    }
    let currentGroupMembers = groupMembers.get(GroupCode);
    let PromiseData = [];
    let ret = /* @__PURE__ */ new Map();
    if (!currentGroupMembers) {
      return ret;
    }
    for (let member of currentGroupMembers.values()) {
      PromiseData.push(getdata(member.uid).catch(() => void 0));
    }
    let allRet = await runAllWithTimeout(PromiseData, 2500);
    for (let PromiseDo of allRet) {
      if (PromiseDo) {
        ret.set(PromiseDo.sendUin, PromiseDo.sendTime);
      }
    }
    return ret;
  }
  static async getLastestMsgByUids(GroupCode, uids) {
    let ret = await napCatCore.session.getMsgService().queryMsgsWithFilterEx("0", "0", "0", {
      chatInfo: {
        peerUid: GroupCode,
        chatType: ChatType.group
      },
      filterMsgType: [],
      filterSendersUid: uids,
      filterMsgToTime: "0",
      filterMsgFromTime: "0",
      isReverseOrder: false,
      isIncludeCurrent: true,
      pageLimit: 1
    });
    return ret;
  }
  static async getGroupMemberAll(GroupCode, forced = false) {
    return napCatCore.session.getGroupService().getAllMemberList(GroupCode, forced);
  }
  static async getLastestMsg(GroupCode, uins) {
    let uids = [];
    for (let uin of uins) {
      let uid = await NTQQUserApi.getUidByUin(uin);
      if (uid) {
        uids.push(uid);
      }
    }
    let ret = await napCatCore.session.getMsgService().queryMsgsWithFilterEx("0", "0", "0", {
      chatInfo: {
        peerUid: GroupCode,
        chatType: ChatType.group
      },
      filterMsgType: [],
      filterSendersUid: uids,
      filterMsgToTime: "0",
      filterMsgFromTime: "0",
      isReverseOrder: false,
      isIncludeCurrent: true,
      pageLimit: 1
    });
    return ret;
  }
  static async getGroupRecommendContactArkJson(GroupCode) {
    return napCatCore.session.getGroupService().getGroupRecommendContactArkJson(GroupCode);
  }
  static async CreatGroupFileFolder(groupCode, folderName) {
    return napCatCore.session.getRichMediaService().createGroupFolder(groupCode, folderName);
  }
  static async DelGroupFile(groupCode, files) {
    return napCatCore.session.getRichMediaService().deleteGroupFile(groupCode, [102], files);
  }
  static async DelGroupFileFolder(groupCode, folderId) {
    return napCatCore.session.getRichMediaService().deleteGroupFolder(groupCode, folderId);
  }
  static async addGroupEssence(GroupCode, msgId) {
    let MsgData = await napCatCore.session.getMsgService().getMsgsIncludeSelf({
      chatType: 2,
      guildId: "",
      peerUid: GroupCode
    }, msgId, 1, false);
    let param = {
      groupCode: GroupCode,
      msgRandom: parseInt(MsgData.msgList[0].msgRandom),
      msgSeq: parseInt(MsgData.msgList[0].msgSeq)
    };
    return napCatCore.session.getGroupService().addGroupEssence(param);
  }
  static async removeGroupEssence(GroupCode, msgId) {
    let MsgData = await napCatCore.session.getMsgService().getMsgsIncludeSelf({
      chatType: 2,
      guildId: "",
      peerUid: GroupCode
    }, msgId, 1, false);
    let param = {
      groupCode: GroupCode,
      msgRandom: parseInt(MsgData.msgList[0].msgRandom),
      msgSeq: parseInt(MsgData.msgList[0].msgSeq)
    };
    return napCatCore.session.getGroupService().removeGroupEssence(param);
  }
  static async getSingleScreenNotifies(num) {
    let [_retData, _doubt, _seq, notifies] = await NTEventDispatch.CallNormalEvent("NodeIKernelGroupService/getSingleScreenNotifies", "NodeIKernelGroupListener/onGroupSingleScreenNotifies", 1, 5e3, () => true, false, "", num);
    return notifies;
  }
  static async getGroupMemberV2(GroupCode, uid, forced = false) {
    const [ret, _groupCode, _changeType, _members] = await NTEventDispatch.CallNormalEvent("NodeIKernelGroupService/getMemberInfo", "NodeIKernelGroupListener/onMemberInfoChange", 1, 5e3, (groupCode, changeType, members) => {
      return groupCode == GroupCode && members.has(uid);
    }, GroupCode, [uid], forced);
    return _members.get(uid);
  }
  static async getGroupMembers(groupQQ, num = 3e3) {
    const groupService = napCatCore.session.getGroupService();
    const sceneId = groupService.createMemberListScene(groupQQ, "groupMemberList_MainWindow");
    const result = await groupService.getNextMemberList(sceneId, void 0, num);
    if (result.errCode !== 0) {
      throw "获取群成员列表出错," + result.errMsg;
    }
    return result.result.infos;
  }
  static async getGroupNotifies() {
  }
  static async GetGroupFileCount(Gids) {
    return napCatCore.session.getRichMediaService().batchGetGroupFileCount(Gids);
  }
  static async getGroupIgnoreNotifies() {
  }
  static async getArkJsonGroupShare(GroupCode) {
    let ret = await NTEventDispatch.CallNoListenerEvent("NodeIKernelGroupService/getGroupRecommendContactArkJson", 5e3, GroupCode);
    return ret.arkJson;
  }
  //需要异常处理
  static async uploadGroupBulletinPic(GroupCode, imageurl) {
    const _Pskey = (await NTQQUserApi.getPSkey(["qun.qq.com"])).domainPskeyMap.get("qun.qq.com");
    return napCatCore.session.getGroupService().uploadGroupBulletinPic(GroupCode, _Pskey, imageurl);
  }
  static async handleGroupRequest(flag, operateType, reason) {
    let flagitem = flag.split("|");
    let groupCode = flagitem[0];
    let seq = flagitem[1];
    let type = parseInt(flagitem[2]);
    return napCatCore.session.getGroupService().operateSysNotify(false, {
      "operateType": operateType,
      // 2 拒绝
      "targetMsg": {
        "seq": seq,
        // 通知序列号
        "type": type,
        "groupCode": groupCode,
        "postscript": reason || " "
        // 仅传空值可能导致处理失败，故默认给个空格
      }
    });
  }
  static async quitGroup(groupQQ) {
    return napCatCore.session.getGroupService().quitGroup(groupQQ);
  }
  static async kickMember(groupQQ, kickUids, refuseForever = false, kickReason = "") {
    return napCatCore.session.getGroupService().kickMember(groupQQ, kickUids, refuseForever, kickReason);
  }
  static async banMember(groupQQ, memList) {
    return napCatCore.session.getGroupService().setMemberShutUp(groupQQ, memList);
  }
  static async banGroup(groupQQ, shutUp) {
    return napCatCore.session.getGroupService().setGroupShutUp(groupQQ, shutUp);
  }
  static async setMemberCard(groupQQ, memberUid, cardName) {
    return napCatCore.session.getGroupService().modifyMemberCardName(groupQQ, memberUid, cardName);
  }
  static async setMemberRole(groupQQ, memberUid, role) {
    return napCatCore.session.getGroupService().modifyMemberRole(groupQQ, memberUid, role);
  }
  static async setGroupName(groupQQ, groupName) {
    return napCatCore.session.getGroupService().modifyGroupName(groupQQ, groupName, false);
  }
  // 头衔不可用
  static async setGroupTitle(groupQQ, uid, title) {
  }
  static async publishGroupBulletin(groupQQ, content, picInfo = void 0, pinned = 0, confirmRequired = 0) {
    const _Pskey = (await NTQQUserApi.getPSkey(["qun.qq.com"])).domainPskeyMap.get("qun.qq.com");
    let data = {
      text: encodeURI(content),
      picInfo,
      oldFeedsId: "",
      pinned,
      confirmRequired
    };
    return napCatCore.session.getGroupService().publishGroupBulletin(groupQQ, _Pskey, data);
  }
  static async getGroupRemainAtTimes(GroupCode) {
    napCatCore.session.getGroupService().getGroupRemainAtTimes(GroupCode);
  }
  static async getMemberExtInfo(groupCode, uin) {
    return napCatCore.session.getGroupService().getMemberExtInfo({
      groupCode,
      sourceType: MemberExtSourceType.TITLETYPE,
      beginUin: "0",
      dataTime: "0",
      uinList: [uin],
      uinNum: "",
      seq: "",
      groupType: "",
      richCardNameVer: "",
      memberExtFilter: {
        memberLevelInfoUin: 1,
        memberLevelInfoPoint: 1,
        memberLevelInfoActiveDay: 1,
        memberLevelInfoLevel: 1,
        memberLevelInfoName: 1,
        levelName: 1,
        dataTime: 1,
        userShowFlag: 1,
        sysShowFlag: 1,
        timeToUpdate: 1,
        nickName: 1,
        specialTitle: 1,
        levelNameNew: 1,
        userShowFlagNew: 1,
        msgNeedField: 1,
        cmdUinFlagExt3Grocery: 1,
        memberIcon: 1,
        memberInfoSeq: 1
      }
    });
  }
}, _applyDecoratedDescriptor$2(_class$2, "getGroupMemberLastestSendTimeCache", [_dec$2], Object.getOwnPropertyDescriptor(_class$2, "getGroupMemberLastestSendTimeCache"), _class$2), _class$2);

async function LoadMessageIdList(Peer, msgId) {
  let msgList = await NTQQMsgApi.getMsgHistory(Peer, msgId, 50);
  for (let j = 0; j < msgList.msgList.length; j++) {
    MessageUnique.createMsg(Peer, msgList.msgList[j].msgId);
  }
}
async function loadMessageUnique() {
  if (groups.size > 100) {
    logWarn("[性能检测] 群数量大于100，可能会导致性能问题");
  }
  let predict = (groups.size + friends.size / 2) / 5;
  predict = predict < 20 ? 20 : predict;
  predict = predict > 50 ? 50 : predict;
  predict = Math.floor(predict * 50);
  MessageUnique.resize(predict);
  let RecentContact = await NTQQUserApi.getRecentContactListSnapShot(predict);
  let LoadMessageIdDo = new Array();
  if (RecentContact?.info?.changedList && RecentContact?.info?.changedList?.length > 0) {
    for (let i = 0; i < RecentContact.info.changedList.length; i++) {
      let Peer = {
        chatType: RecentContact.info.changedList[i].chatType,
        peerUid: RecentContact.info.changedList[i].peerUid,
        guildId: ""
      };
      LoadMessageIdDo.push(LoadMessageIdList(Peer, RecentContact.info.changedList[i].msgId));
    }
  }
  await Promise.all(LoadMessageIdDo).then(() => {
    log(`[消息序列] 加载 ${predict} 条历史消息记录完成`);
  });
}
setTimeout(() => {
  napCatCore.onLoginSuccess(async () => {
    await sleep(100);
    loadMessageUnique().then().catch();
  });
}, 100);
class NTQQMsgApi {
  static async FetchLongMsg(peer, msgId) {
    return napCatCore.session.getMsgService().fetchLongMsg(peer, msgId);
  }
  static async getTempChatInfo(chatType, peerUid) {
    return napCatCore.session.getMsgService().getTempChatInfo(chatType, peerUid);
  }
  static async PrepareTempChat(toUserUid, GroupCode, nickname) {
    let TempGameSession = {
      nickname: "",
      gameAppId: "",
      selfTinyId: "",
      peerRoleId: "",
      peerOpenId: ""
    };
    return napCatCore.session.getMsgService().prepareTempChat({
      chatType: ChatType2.KCHATTYPETEMPC2CFROMGROUP,
      peerUid: toUserUid,
      peerNickname: nickname,
      fromGroupCode: GroupCode,
      sig: "",
      selfPhone: "",
      selfUid: selfInfo.uid,
      gameSession: TempGameSession
    });
  }
  static async getMsgEmojiLikesList(peer, msgSeq, emojiId, emojiType, count = 20) {
    return napCatCore.session.getMsgService().getMsgEmojiLikesList(peer, msgSeq, emojiId, emojiType, "", false, 20);
  }
  // static napCatCore: NapCatCore | null = null;
  //   enum BaseEmojiType {
  //     NORMAL_EMOJI,
  //     SUPER_EMOJI,
  //     RANDOM_SUPER_EMOJI,
  //     CHAIN_SUPER_EMOJI,
  //     EMOJI_EMOJI
  // }
  static async setEmojiLike(peer, msgSeq, emojiId, set = true) {
    emojiId = emojiId.toString();
    return napCatCore.session.getMsgService().setMsgEmojiLikes(peer, msgSeq, emojiId, emojiId.length > 3 ? "2" : "1", set);
  }
  static async getMultiMsg(peer, rootMsgId, parentMsgId) {
    return napCatCore.session.getMsgService().getMultiMsg(peer, rootMsgId, parentMsgId);
  }
  static async ForwardMsg(peer, msgIds) {
    return napCatCore.session.getMsgService().forwardMsg(msgIds, peer, [peer], []);
  }
  static async getLastestMsgByUids(peer, count = 20, isReverseOrder = false) {
    let ret = await napCatCore.session.getMsgService().queryMsgsWithFilterEx("0", "0", "0", {
      chatInfo: peer,
      filterMsgType: [],
      filterSendersUid: [],
      filterMsgToTime: "0",
      filterMsgFromTime: "0",
      isReverseOrder,
      //此参数有点离谱 注意不是本次查询的排序 而是全部消历史信息的排序 默认false 从新消息拉取到旧消息
      isIncludeCurrent: true,
      pageLimit: count
    });
    return ret;
  }
  static async getMsgsByMsgId(peer, msgIds) {
    if (!peer) throw new Error("peer is not allowed");
    if (!msgIds) throw new Error("msgIds is not allowed");
    return await napCatCore.session.getMsgService().getMsgsByMsgId(peer, msgIds);
  }
  static async getSingleMsg(peer, seq) {
    return await napCatCore.session.getMsgService().getSingleMsg(peer, seq);
  }
  static async fetchFavEmojiList(num) {
    return napCatCore.session.getMsgService().fetchFavEmojiList("", num, true, true);
  }
  static async queryMsgsWithFilterExWithSeq(peer, msgSeq) {
    let ret = await napCatCore.session.getMsgService().queryMsgsWithFilterEx("0", "0", msgSeq, {
      chatInfo: peer,
      //此处为Peer 为关键查询参数 没有啥也没有 by mlik iowa
      filterMsgType: [],
      filterSendersUid: [],
      filterMsgToTime: "0",
      filterMsgFromTime: "0",
      isReverseOrder: false,
      isIncludeCurrent: true,
      pageLimit: 1
    });
    return ret;
  }
  /**
   * 
   * @deprecated 从9.9.15-26702版本开始，该接口已经废弃，请使用getMsgsEx
   * @param peer 
   * @param seq 
   * @param count 
   * @param desc 
   * @param z 
   * @returns 
   */
  static async getMsgsBySeqAndCount(peer, seq, count, desc, z) {
    return await napCatCore.session.getMsgService().getMsgsBySeqAndCount(peer, seq, count, desc, z);
  }
  static async setMsgRead(peer) {
    return napCatCore.session.getMsgService().setMsgRead(peer);
  }
  static async getGroupFileList(GroupCode, params) {
    let data = await NTEventDispatch.CallNormalEvent("NodeIKernelRichMediaService/getGroupFileList", "NodeIKernelMsgListener/onGroupFileInfoUpdate", 1, 5e3, (groupFileListResult) => {
      return true;
    }, GroupCode, params);
    return data[1].item;
  }
  static async getMsgHistory(peer, msgId, count, isReverseOrder = false) {
    return napCatCore.session.getMsgService().getMsgsIncludeSelf(peer, msgId, count, isReverseOrder);
  }
  static async recallMsg(peer, msgIds) {
    await napCatCore.session.getMsgService().recallMsg({
      chatType: peer.chatType,
      peerUid: peer.peerUid
    }, msgIds);
  }
  static async sendMsgV2(peer, msgElements, waitComplete = true, timeout = 1e4) {
    if (peer.chatType === ChatType.temp) ;
    function generateMsgId() {
      const timestamp = Math.floor(Date.now() / 1e3);
      const random = Math.floor(Math.random() * Math.pow(2, 32));
      const buffer = Buffer.alloc(8);
      buffer.writeUInt32BE(timestamp, 0);
      buffer.writeUInt32BE(random, 4);
      const msgId2 = BigInt("0x" + buffer.toString("hex")).toString();
      return msgId2;
    }
    let msgId;
    try {
      msgId = await NTQQMsgApi.getMsgUnique(peer.chatType, await NTQQMsgApi.getServerTime());
    } catch (error) {
      msgId = generateMsgId().toString();
    }
    let data = await NTEventDispatch.CallNormalEvent("NodeIKernelMsgService/sendMsg", "NodeIKernelMsgListener/onMsgInfoListUpdate", 1, timeout, (msgRecords) => {
      for (let msgRecord of msgRecords) {
        if (msgRecord.msgId === msgId && msgRecord.sendStatus === 2) {
          return true;
        }
      }
      return false;
    }, msgId, peer, msgElements, /* @__PURE__ */ new Map());
    let retMsg = data[1].find((msgRecord) => {
      if (msgRecord.msgId === msgId) {
        return true;
      }
    });
    return retMsg;
  }
  static sendMsgEx(peer, msgElements, waitComplete = true, timeout = 1e4) {
  }
  static async sendMsg(peer, msgElements, waitComplete = true, timeout = 1e4) {
    function generateMsgId() {
      const timestamp = Math.floor(Date.now() / 1e3);
      const random = Math.floor(Math.random() * Math.pow(2, 32));
      const buffer = Buffer.alloc(8);
      buffer.writeUInt32BE(timestamp, 0);
      buffer.writeUInt32BE(random, 4);
      const msgId2 = BigInt("0x" + buffer.toString("hex")).toString();
      return msgId2;
    }
    let msgId;
    try {
      msgId = await NTQQMsgApi.getMsgUnique(peer.chatType, await NTQQMsgApi.getServerTime());
    } catch (error) {
      msgId = generateMsgId();
    }
    if (peer.chatType === ChatType.temp && peer.guildId && peer.guildId !== "") {
      let member = await getGroupMember(peer.guildId, peer.peerUid);
      if (member) {
        await NTQQMsgApi.PrepareTempChat(peer.peerUid, peer.guildId, member.nick);
      }
    }
    peer.guildId = msgId;
    let data = await NTEventDispatch.CallNormalEvent("NodeIKernelMsgService/sendMsg", "NodeIKernelMsgListener/onMsgInfoListUpdate", 1, timeout, (msgRecords) => {
      for (let msgRecord of msgRecords) {
        if (msgRecord.guildId === msgId && msgRecord.sendStatus === 2) {
          return true;
        }
      }
      return false;
    }, "0", peer, msgElements, /* @__PURE__ */ new Map());
    let retMsg = data[1].find((msgRecord) => {
      if (msgRecord.guildId === msgId) {
        return true;
      }
    });
    return retMsg;
  }
  static async getMsgUnique(chatType, time) {
    if (requireMinNTQQBuild("26702")) {
      return napCatCore.session.getMsgService().generateMsgUniqueId(chatType, time);
    }
    return napCatCore.session.getMsgService().getMsgUniqueId(time);
  }
  static async getServerTime() {
    return napCatCore.session.getMSFService().getServerTime();
  }
  static async getServerTimeV2() {
    return NTEventDispatch.CallNoListenerEvent("NodeIKernelMsgService/getServerTime", 5e3);
  }
  static async forwardMsg(srcPeer, destPeer, msgIds) {
    return napCatCore.session.getMsgService().forwardMsg(msgIds, srcPeer, [destPeer], []);
  }
  static async multiForwardMsg(srcPeer, destPeer, msgIds) {
    const msgInfos = msgIds.map((id) => {
      return {
        msgId: id,
        senderShowName: selfInfo.nick
      };
    });
    let data = await NTEventDispatch.CallNormalEvent("NodeIKernelMsgService/multiForwardMsgWithComment", "NodeIKernelMsgListener/onMsgInfoListUpdate", 1, 5e3, (msgRecords) => {
      for (let msgRecord of msgRecords) {
        if (msgRecord.peerUid == destPeer.peerUid && msgRecord.senderUid == selfInfo.uid) {
          return true;
        }
      }
      return false;
    }, msgInfos, srcPeer, destPeer, [], /* @__PURE__ */ new Map());
    for (let msg of data[1]) {
      const arkElement = msg.elements.find((ele) => ele.arkElement);
      if (!arkElement) {
        continue;
      }
      const forwardData = JSON.parse(arkElement.arkElement.bytesData);
      if (forwardData.app != "com.tencent.multimsg") {
        continue;
      }
      if (msg.peerUid == destPeer.peerUid && msg.senderUid == selfInfo.uid) {
        return msg;
      }
    }
    throw new Error("转发消息超时");
  }
  static async markallMsgAsRead() {
    return napCatCore.session.getMsgService().setAllC2CAndGroupMsgRead();
  }
}

let BuddyListReqType = /* @__PURE__ */ function(BuddyListReqType2) {
  BuddyListReqType2[BuddyListReqType2["KNOMAL"] = 0] = "KNOMAL";
  BuddyListReqType2[BuddyListReqType2["KLETTER"] = 1] = "KLETTER";
  return BuddyListReqType2;
}({});

let UserDetailSource = /* @__PURE__ */ function(UserDetailSource2) {
  UserDetailSource2[UserDetailSource2["KDB"] = 0] = "KDB";
  UserDetailSource2[UserDetailSource2["KSERVER"] = 1] = "KSERVER";
  return UserDetailSource2;
}({});
let ProfileBizType = /* @__PURE__ */ function(ProfileBizType2) {
  ProfileBizType2[ProfileBizType2["KALL"] = 0] = "KALL";
  ProfileBizType2[ProfileBizType2["KBASEEXTEND"] = 1] = "KBASEEXTEND";
  ProfileBizType2[ProfileBizType2["KVAS"] = 2] = "KVAS";
  ProfileBizType2[ProfileBizType2["KQZONE"] = 3] = "KQZONE";
  ProfileBizType2[ProfileBizType2["KOTHER"] = 4] = "KOTHER";
  return ProfileBizType2;
}({});

var _dec$1, _dec2$1, _dec3$1, _dec4, _dec5, _dec6, _dec7, _class$1;
function _applyDecoratedDescriptor$1(i, e, r, n, l) {
  var a = {};
  return Object.keys(n).forEach(function(i2) {
    a[i2] = n[i2];
  }), a.enumerable = !!a.enumerable, a.configurable = !!a.configurable, ("value" in a || a.initializer) && (a.writable = true), a = r.slice().reverse().reduce(function(r2, n2) {
    return n2(i, e, r2) || r2;
  }, a), l && void 0 !== a.initializer && (a.value = a.initializer ? a.initializer.call(l) : void 0, a.initializer = void 0), void 0 === a.initializer ? (Object.defineProperty(i, e, a), null) : a;
}
let NTQQUserApi = (_dec$1 = CacheClassFuncAsync(1800 * 1e3), _dec2$1 = CacheClassFuncAsync(1800 * 1e3), _dec3$1 = CacheClassFuncAsync(1800 * 1e3), _dec4 = CacheClassFuncAsync(1800 * 1e3), _dec5 = CacheClassFuncAsyncExtend(3600 * 1e3, "Uin2Uid", (Uin, Uid) => {
  if (Uid && Uid.indexOf("u_") != -1) {
    return true;
  }
  logWarn("uin转换到uid时异常", Uin, Uid);
  return false;
}), _dec6 = CacheClassFuncAsyncExtend(3600 * 1e3, "Uid2Uin", (Uid, Uin) => {
  if (Uin && Uin != 0 && !isNaN(Uin)) {
    return true;
  }
  logWarn("uid转换到uin时异常", Uid, Uin);
  return false;
}), _dec7 = CacheClassFuncAsync(3600 * 1e3, "ClientKey"), _class$1 = class NTQQUserApi2 {
  static async getProfileLike(uid) {
    return napCatCore.session.getProfileLikeService().getBuddyProfileLike({
      friendUids: [uid],
      basic: 1,
      vote: 1,
      favorite: 0,
      userProfile: 1,
      type: 2,
      start: 0,
      limit: 20
    });
  }
  static async setLongNick(longNick) {
    return napCatCore.session.getProfileService().setLongNick(longNick);
  }
  static async setSelfOnlineStatus(status, extStatus, batteryStatus) {
    return napCatCore.session.getMsgService().setStatus({
      status,
      extStatus,
      batteryStatus
    });
  }
  static async getBuddyRecommendContactArkJson(uin, sencenID = "") {
    return napCatCore.session.getBuddyService().getBuddyRecommendContactArkJson(uin, sencenID);
  }
  static async like(uid, count = 1) {
    return napCatCore.session.getProfileLikeService().setBuddyProfileLike({
      friendUid: uid,
      sourceId: 71,
      doLikeCount: count,
      doLikeTollCount: 0
    });
  }
  static async setQQAvatar(filePath) {
    const ret = await napCatCore.session.getProfileService().setHeader(filePath);
    return {
      result: ret?.result,
      errMsg: ret?.errMsg
    };
  }
  static async setGroupAvatar(gc, filePath) {
    return napCatCore.session.getGroupService().setHeader(gc, filePath);
  }
  static async fetchUserDetailInfos(uids) {
    let retData = [];
    await NTEventDispatch.CallNormalEvent("NodeIKernelProfileService/fetchUserDetailInfo", "NodeIKernelProfileListener/onUserDetailInfoChanged", uids.length, 5e3, (profile) => {
      if (uids.includes(profile.uid)) {
        let RetUser = {
          ...profile.simpleInfo.coreInfo,
          ...profile.simpleInfo.status,
          ...profile.simpleInfo.vasInfo,
          ...profile.commonExt,
          ...profile.simpleInfo.baseInfo,
          qqLevel: profile.commonExt.qqLevel,
          pendantId: ""
        };
        retData.push(RetUser);
        return true;
      }
      return false;
    }, "BuddyProfileStore", uids, UserDetailSource.KSERVER, [ProfileBizType.KALL]);
    return retData;
  }
  static async fetchUserDetailInfo(uid) {
    let [_retData, profile] = await NTEventDispatch.CallNormalEvent("NodeIKernelProfileService/fetchUserDetailInfo", "NodeIKernelProfileListener/onUserDetailInfoChanged", 1, 5e3, (profile2) => {
      if (profile2.uid === uid) {
        return true;
      }
      return false;
    }, "BuddyProfileStore", [uid], UserDetailSource.KSERVER, [ProfileBizType.KALL]);
    let RetUser = {
      ...profile.simpleInfo.coreInfo,
      ...profile.simpleInfo.status,
      ...profile.simpleInfo.vasInfo,
      ...profile.commonExt,
      ...profile.simpleInfo.baseInfo,
      qqLevel: profile.commonExt.qqLevel,
      pendantId: ""
    };
    return RetUser;
  }
  static async getUserDetailInfo(uid) {
    if (requireMinNTQQBuild("26702")) {
      return this.fetchUserDetailInfo(uid);
    }
    return this.getUserDetailInfoOld(uid);
  }
  static async getUserDetailInfoOld(uid) {
    let [_retData, profile] = await NTEventDispatch.CallNormalEvent("NodeIKernelProfileService/getUserDetailInfoWithBizInfo", "NodeIKernelProfileListener/onProfileDetailInfoChanged", 2, 5e3, (profile2) => {
      if (profile2.uid === uid) {
        return true;
      }
      return false;
    }, uid, [0]);
    return profile;
  }
  static async modifySelfProfile(param) {
    return napCatCore.session.getProfileService().modifyDesktopMiniProfile(param);
  }
  //需要异常处理
  static async getCookies(domain) {
    const ClientKeyData = await NTQQUserApi2.forceFetchClientKey();
    const requestUrl = "https://ssl.ptlogin2.qq.com/jump?ptlang=1033&clientuin=" + selfInfo.uin + "&clientkey=" + ClientKeyData.clientKey + "&u1=https%3A%2F%2F" + domain + "%2F" + selfInfo.uin + "%2Finfocenter&keyindex=19%27";
    let cookies = await RequestUtil.HttpsGetCookies(requestUrl);
    return cookies;
  }
  static async getPSkey(domainList) {
    return await napCatCore.session.getTipOffService().getPskey(domainList, true);
  }
  static async getRobotUinRange() {
    const robotUinRanges = await napCatCore.session.getRobotService().getRobotUinRange({
      justFetchMsgConfig: "1",
      type: 1,
      version: 0,
      aioKeywordVersion: 0
    });
    return robotUinRanges?.response?.robotUinRanges;
  }
  //需要异常处理
  static async getQzoneCookies() {
    const ClientKeyData = await NTQQUserApi2.forceFetchClientKey();
    const requestUrl = "https://ssl.ptlogin2.qq.com/jump?ptlang=1033&clientuin=" + selfInfo.uin + "&clientkey=" + ClientKeyData.clientKey + "&u1=https%3A%2F%2Fuser.qzone.qq.com%2F" + selfInfo.uin + "%2Finfocenter&keyindex=19%27";
    let cookies = await RequestUtil.HttpsGetCookies(requestUrl);
    return cookies;
  }
  //需要异常处理
  static async getSkey() {
    const ClientKeyData = await NTQQUserApi2.forceFetchClientKey();
    if (ClientKeyData.result !== 0) {
      throw new Error("getClientKey Error");
    }
    const clientKey = ClientKeyData.clientKey;
    ClientKeyData.keyIndex;
    const requestUrl = "https://ssl.ptlogin2.qq.com/jump?ptlang=1033&clientuin=" + selfInfo.uin + "&clientkey=" + clientKey + "&u1=https%3A%2F%2Fh5.qzone.qq.com%2Fqqnt%2Fqzoneinpcqq%2Ffriend%3Frefresh%3D0%26clientuin%3D0%26darkMode%3D0&keyindex=19%27";
    let cookies = await RequestUtil.HttpsGetCookies(requestUrl);
    const skey = cookies["skey"];
    if (!skey) {
      throw new Error("getSkey Skey is Empty");
    }
    return skey;
  }
  static async getUidByUin(Uin) {
    if (requireMinNTQQBuild("26702")) {
      return await NTQQUserApi2.getUidByUinV2(Uin);
    }
    return await NTQQUserApi2.getUidByUinV1(Uin);
  }
  static async getUinByUid(Uid) {
    if (requireMinNTQQBuild("26702")) {
      return await NTQQUserApi2.getUinByUidV2(Uid);
    }
    return await NTQQUserApi2.getUinByUidV1(Uid);
  }
  //后期改成流水线处理
  static async getUidByUinV2(Uin) {
    let uid = (await napCatCore.session.getProfileService().getUidByUin("FriendsServiceImpl", [Uin])).get(Uin);
    if (uid) return uid;
    uid = (await napCatCore.session.getGroupService().getUidByUins([Uin])).uids.get(Uin);
    if (uid) return uid;
    uid = (await napCatCore.session.getUixConvertService().getUid([Uin])).uidInfo.get(Uin);
    if (uid) return uid;
    console.log(await NTQQFriendApi.getBuddyIdMapCache(true));
    uid = (await NTQQFriendApi.getBuddyIdMapCache(true)).getValue(Uin);
    if (uid) return uid;
    uid = (await NTQQFriendApi.getBuddyIdMap(true)).getValue(Uin);
    if (uid) return uid;
    let unveifyUid = (await NTQQUserApi2.getUserDetailInfoByUinV2(Uin)).detail.uid;
    if (unveifyUid.indexOf("*") == -1) uid = unveifyUid;
    return uid;
  }
  //后期改成流水线处理
  static async getUinByUidV2(Uid) {
    let uin = (await napCatCore.session.getProfileService().getUinByUid("FriendsServiceImpl", [Uid])).get(Uid);
    if (uin) return uin;
    uin = (await napCatCore.session.getGroupService().getUinByUids([Uid])).uins.get(Uid);
    if (uin) return uin;
    uin = (await napCatCore.session.getUixConvertService().getUin([Uid])).uinInfo.get(Uid);
    if (uin) return uin;
    uin = (await NTQQFriendApi.getBuddyIdMapCache(true)).getKey(Uid);
    if (uin) return uin;
    uin = (await NTQQFriendApi.getBuddyIdMap(true)).getKey(Uid);
    if (uin) return uin;
    uin = (await NTQQUserApi2.getUserDetailInfo(Uid)).uin;
    return uin;
  }
  static async getUidByUinV1(Uin) {
    let uid = (await napCatCore.session.getUixConvertService().getUid([Uin])).uidInfo.get(Uin);
    if (!uid) {
      Array.from(friends.values()).forEach((t) => {
        if (t.uin == Uin) {
          uid = t.uid;
        }
      });
    }
    if (!uid) {
      for (let groupMembersList of groupMembers.values()) {
        for (let GroupMember of groupMembersList.values()) {
          if (GroupMember.uin == Uin) {
            uid = GroupMember.uid;
          }
        }
      }
    }
    if (!uid) {
      let unveifyUid = (await NTQQUserApi2.getUserDetailInfoByUin(Uin)).info.uid;
      if (unveifyUid.indexOf("*") == -1) {
        uid = unveifyUid;
      }
    }
    return uid;
  }
  static async getUinByUidV1(Uid) {
    let ret = await NTEventDispatch.CallNoListenerEvent("NodeIKernelUixConvertService/getUin", 5e3, [Uid]);
    let uin = ret.uinInfo.get(Uid);
    if (!uin) {
      Array.from(friends.values()).forEach((t) => {
        if (t.uid == Uid) {
          uin = t.uin;
        }
      });
    }
    if (!uin) {
      uin = (await NTQQUserApi2.getUserDetailInfo(Uid)).uin;
    }
    return uin;
  }
  static async getRecentContactListSnapShot(count) {
    return await napCatCore.session.getRecentContactService().getRecentContactListSnapShot(count);
  }
  static async getRecentContactListSyncLimit(count) {
    return await napCatCore.session.getRecentContactService().getRecentContactListSyncLimit(count);
  }
  static async getRecentContactListSync() {
    return await napCatCore.session.getRecentContactService().getRecentContactListSync();
  }
  static async getRecentContactList() {
    return await napCatCore.session.getRecentContactService().getRecentContactList();
  }
  static async getUserDetailInfoByUinV2(Uin) {
    return await NTEventDispatch.CallNoListenerEvent("NodeIKernelProfileService/getUserDetailInfoByUin", 5e3, Uin);
  }
  static async getUserDetailInfoByUin(Uin) {
    return NTEventDispatch.CallNoListenerEvent("NodeIKernelProfileService/getUserDetailInfoByUin", 5e3, Uin);
  }
  static async forceFetchClientKey() {
    return await napCatCore.session.getTicketService().forceFetchClientKey("");
  }
}, _applyDecoratedDescriptor$1(_class$1, "getCookies", [_dec$1], Object.getOwnPropertyDescriptor(_class$1, "getCookies"), _class$1), _applyDecoratedDescriptor$1(_class$1, "getPSkey", [_dec2$1], Object.getOwnPropertyDescriptor(_class$1, "getPSkey"), _class$1), _applyDecoratedDescriptor$1(_class$1, "getQzoneCookies", [_dec3$1], Object.getOwnPropertyDescriptor(_class$1, "getQzoneCookies"), _class$1), _applyDecoratedDescriptor$1(_class$1, "getSkey", [_dec4], Object.getOwnPropertyDescriptor(_class$1, "getSkey"), _class$1), _applyDecoratedDescriptor$1(_class$1, "getUidByUin", [_dec5], Object.getOwnPropertyDescriptor(_class$1, "getUidByUin"), _class$1), _applyDecoratedDescriptor$1(_class$1, "getUinByUid", [_dec6], Object.getOwnPropertyDescriptor(_class$1, "getUinByUid"), _class$1), _applyDecoratedDescriptor$1(_class$1, "forceFetchClientKey", [_dec7], Object.getOwnPropertyDescriptor(_class$1, "forceFetchClientKey"), _class$1), _class$1);

var _dec, _dec2, _dec3, _class;
function _applyDecoratedDescriptor(i, e, r, n, l) {
  var a = {};
  return Object.keys(n).forEach(function(i2) {
    a[i2] = n[i2];
  }), a.enumerable = !!a.enumerable, a.configurable = !!a.configurable, ("value" in a || a.initializer) && (a.writable = true), a = r.slice().reverse().reduce(function(r2, n2) {
    return n2(i, e, r2) || r2;
  }, a), l && void 0 !== a.initializer && (a.value = a.initializer ? a.initializer.call(l) : void 0, a.initializer = void 0), void 0 === a.initializer ? (Object.defineProperty(i, e, a), null) : a;
}
let WebHonorType = /* @__PURE__ */ function(WebHonorType2) {
  WebHonorType2["ALL"] = "all";
  WebHonorType2["TALKACTIVE"] = "talkative";
  WebHonorType2["PERFROMER"] = "performer";
  WebHonorType2["LEGEND"] = "legend";
  WebHonorType2["STORONGE_NEWBI"] = "strong_newbie";
  WebHonorType2["EMOTION"] = "emotion";
  return WebHonorType2;
}({});
let WebApi = (_dec = CacheClassFuncAsync(3600 * 1e3, "webapi_get_group_members"), _dec2 = CacheClassFuncAsync(3600 * 1e3, "webapi_get_group_members"), _dec3 = CacheClassFuncAsync(3600 * 1e3, "GroupHonorInfo"), _class = class WebApi2 {
  static async shareDigest(groupCode, msgSeq, msgRandom, targetGroupCode) {
    const CookiesObject = await NTQQUserApi.getCookies("qun.qq.com");
    const CookieValue = Object.entries(CookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
    const Bkn = WebApi2.genBkn(CookiesObject.skey);
    let ret = void 0;
    const data = "group_code=" + groupCode + "&msg_seq=" + msgSeq + "&msg_random=" + msgRandom + "&target_group_code=" + targetGroupCode;
    const url = "https://qun.qq.com/cgi-bin/group_digest/share_digest?bkn=" + Bkn + "&" + data;
    try {
      ret = await RequestUtil.HttpGetText(url, "GET", "", {
        "Cookie": CookieValue
      });
      return ret;
    } catch (e) {
      return void 0;
    }
    return void 0;
  }
  static async getGroupEssenceMsg(GroupCode, page_start) {
    const CookiesObject = await NTQQUserApi.getCookies("qun.qq.com");
    const CookieValue = Object.entries(CookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
    const Bkn = WebApi2.genBkn(CookiesObject.skey);
    const url = "https://qun.qq.com/cgi-bin/group_digest/digest_list?bkn=" + Bkn + "&group_code=" + GroupCode + "&page_start=" + page_start + "&page_limit=20";
    let ret;
    try {
      ret = await RequestUtil.HttpGetJson(url, "GET", "", {
        "Cookie": CookieValue
      });
    } catch {
      return void 0;
    }
    if (ret.retcode !== 0) {
      return void 0;
    }
    return ret;
  }
  static async getGroupMembers(GroupCode, cached = true) {
    let MemberData = new Array();
    try {
      const CookiesObject = await NTQQUserApi.getCookies("qun.qq.com");
      const CookieValue = Object.entries(CookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
      const Bkn = WebApi2.genBkn(CookiesObject.skey);
      const retList = [];
      const fastRet = await RequestUtil.HttpGetJson("https://qun.qq.com/cgi-bin/qun_mgr/search_group_members?st=0&end=40&sort=1&gc=" + GroupCode + "&bkn=" + Bkn, "POST", "", {
        "Cookie": CookieValue
      });
      if (!fastRet?.count || fastRet?.errcode !== 0 || !fastRet?.mems) {
        return [];
      } else {
        for (const key in fastRet.mems) {
          MemberData.push(fastRet.mems[key]);
        }
      }
      const PageNum = Math.ceil(fastRet.count / 40);
      for (let i = 2; i <= PageNum; i++) {
        const ret = RequestUtil.HttpGetJson("https://qun.qq.com/cgi-bin/qun_mgr/search_group_members?st=" + (i - 1) * 40 + "&end=" + i * 40 + "&sort=1&gc=" + GroupCode + "&bkn=" + Bkn, "POST", "", {
          "Cookie": CookieValue
        });
        retList.push(ret);
      }
      for (let i = 1; i <= PageNum; i++) {
        const ret = await retList[i];
        if (!ret?.count || ret?.errcode !== 0 || !ret?.mems) {
          continue;
        }
        for (const key in ret.mems) {
          MemberData.push(ret.mems[key]);
        }
      }
    } catch {
      return MemberData;
    }
    return MemberData;
  }
  // public static async addGroupDigest(groupCode: string, msgSeq: string) {
  //   const url = `https://qun.qq.com/cgi-bin/group_digest/cancel_digest?random=665&X-CROSS-ORIGIN=fetch&group_code=${groupCode}&msg_seq=${msgSeq}&msg_random=444021292`;
  //   const res = await this.request(url);
  //   return await res.json();
  // }
  // public async getGroupDigest(groupCode: string) {
  //   const url = `https://qun.qq.com/cgi-bin/group_digest/digest_list?random=665&X-CROSS-ORIGIN=fetch&group_code=${groupCode}&page_start=0&page_limit=20`;
  //   const res = await this.request(url);
  //   return await res.json();
  // }
  static async setGroupNotice(GroupCode, Content = "") {
    const CookiesObject = await NTQQUserApi.getCookies("qun.qq.com");
    const CookieValue = Object.entries(CookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
    const Bkn = WebApi2.genBkn(CookiesObject.skey);
    let ret = void 0;
    const url = "https://web.qun.qq.com/cgi-bin/announce/add_qun_notice?bkn=" + Bkn;
    try {
      ret = await RequestUtil.HttpGetJson(url, "GET", "", {
        "Cookie": CookieValue
      });
      return ret;
    } catch (e) {
      return void 0;
    }
    return void 0;
  }
  static async getGrouptNotice(GroupCode) {
    const CookiesObject = await NTQQUserApi.getCookies("qun.qq.com");
    const CookieValue = Object.entries(CookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
    const Bkn = WebApi2.genBkn(CookiesObject.skey);
    let ret = void 0;
    const url = "https://web.qun.qq.com/cgi-bin/announce/get_t_list?bkn=" + Bkn + "&qid=" + GroupCode + "&ft=23&ni=1&n=1&i=1&log_read=1&platform=1&s=-1&n=20";
    try {
      ret = await RequestUtil.HttpGetJson(url, "GET", "", {
        "Cookie": CookieValue
      });
      if (ret?.ec !== 0) {
        return void 0;
      }
      return ret;
    } catch (e) {
      return void 0;
    }
    return void 0;
  }
  static genBkn(sKey) {
    sKey = sKey || "";
    let hash = 5381;
    for (let i = 0; i < sKey.length; i++) {
      const code = sKey.charCodeAt(i);
      hash = hash + (hash << 5) + code;
    }
    return (hash & 2147483647).toString();
  }
  static async getGroupHonorInfo(groupCode, getType) {
    const CookiesObject = await NTQQUserApi.getCookies("qun.qq.com");
    const CookieValue = Object.entries(CookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
    WebApi2.genBkn(CookiesObject.skey);
    async function getDataInternal(Internal_groupCode, Internal_type) {
      let url = "https://qun.qq.com/interactive/honorlist?gc=" + Internal_groupCode + "&type=" + Internal_type.toString();
      let res = "";
      let resJson;
      try {
        res = await RequestUtil.HttpGetText(url, "GET", "", {
          "Cookie": CookieValue
        });
        const match = res.match(/window\.__INITIAL_STATE__=(.*?);/);
        if (match) {
          resJson = JSON.parse(match[1].trim());
        }
        if (Internal_type === 1) {
          return resJson?.talkativeList;
        } else {
          return resJson?.actorList;
        }
      } catch (e) {
        logDebug("获取当前群荣耀失败", url, e);
      }
      return void 0;
    }
    let HonorInfo = {
      group_id: groupCode
    };
    if (getType === WebHonorType.TALKACTIVE || getType === WebHonorType.ALL) {
      try {
        let RetInternal = await getDataInternal(groupCode, 1);
        if (!RetInternal) {
          throw new Error("获取龙王信息失败");
        }
        HonorInfo.current_talkative = {
          user_id: RetInternal[0]?.uin,
          avatar: RetInternal[0]?.avatar,
          nickname: RetInternal[0]?.name,
          day_count: 0,
          description: RetInternal[0]?.desc
        };
        HonorInfo.talkative_list = [];
        for (const talkative_ele of RetInternal) {
          HonorInfo.talkative_list.push({
            user_id: talkative_ele?.uin,
            avatar: talkative_ele?.avatar,
            description: talkative_ele?.desc,
            day_count: 0,
            nickname: talkative_ele?.name
          });
        }
      } catch (e) {
        logDebug(e);
      }
    }
    if (getType === WebHonorType.PERFROMER || getType === WebHonorType.ALL) {
      try {
        let RetInternal = await getDataInternal(groupCode, 2);
        if (!RetInternal) {
          throw new Error("获取群聊之火失败");
        }
        HonorInfo.performer_list = [];
        for (const performer_ele of RetInternal) {
          HonorInfo.performer_list.push({
            user_id: performer_ele?.uin,
            nickname: performer_ele?.name,
            avatar: performer_ele?.avatar,
            description: performer_ele?.desc
          });
        }
      } catch (e) {
        logDebug(e);
      }
    }
    if (getType === WebHonorType.PERFROMER || getType === WebHonorType.ALL) {
      try {
        let RetInternal = await getDataInternal(groupCode, 3);
        if (!RetInternal) {
          throw new Error("获取群聊炽焰失败");
        }
        HonorInfo.legend_list = [];
        for (const legend_ele of RetInternal) {
          HonorInfo.legend_list.push({
            user_id: legend_ele?.uin,
            nickname: legend_ele?.name,
            avatar: legend_ele?.avatar,
            desc: legend_ele?.description
          });
        }
      } catch (e) {
        logDebug("获取群聊炽焰失败", e);
      }
    }
    if (getType === WebHonorType.EMOTION || getType === WebHonorType.ALL) {
      try {
        let RetInternal = await getDataInternal(groupCode, 6);
        if (!RetInternal) {
          throw new Error("获取快乐源泉失败");
        }
        HonorInfo.emotion_list = [];
        for (const emotion_ele of RetInternal) {
          HonorInfo.emotion_list.push({
            user_id: emotion_ele?.uin,
            nickname: emotion_ele?.name,
            avatar: emotion_ele?.avatar,
            desc: emotion_ele?.description
          });
        }
      } catch (e) {
        logDebug("获取快乐源泉失败", e);
      }
    }
    if (getType === WebHonorType.EMOTION || getType === WebHonorType.ALL) {
      HonorInfo.strong_newbie_list = [];
    }
    return HonorInfo;
  }
}, _applyDecoratedDescriptor(_class, "getGroupEssenceMsg", [_dec], Object.getOwnPropertyDescriptor(_class, "getGroupEssenceMsg"), _class), _applyDecoratedDescriptor(_class, "getGroupMembers", [_dec2], Object.getOwnPropertyDescriptor(_class, "getGroupMembers"), _class), _applyDecoratedDescriptor(_class, "getGroupHonorInfo", [_dec3], Object.getOwnPropertyDescriptor(_class, "getGroupHonorInfo"), _class), _class);

async function SignMiniApp(CardData) {
  let signCard = {
    "app": "com.tencent.miniapp.lua",
    "bizsrc": "tianxuan.imgJumpArk",
    "view": "miniapp",
    "prompt": CardData.prompt,
    "config": {
      "type": "normal",
      "forward": 1,
      "autosize": 0
    },
    "meta": {
      "miniapp": {
        "title": CardData.title,
        "preview": CardData.preview.replace(/\\/g, "\\/\\/"),
        "jumpUrl": CardData.jumpUrl.replace(/\\/g, "\\/\\/"),
        "tag": CardData.tag,
        "tagIcon": CardData.tagIcon.replace(/\\/g, "\\/\\/"),
        "source": CardData.source,
        "sourcelogo": CardData.sourcelogo.replace(/\\/g, "\\/\\/")
      }
    }
  };
  let data = await NTQQUserApi.getQzoneCookies();
  const Bkn = WebApi.genBkn(data.p_skey);
  const CookieValue = "p_skey=" + data.p_skey + "; skey=" + data.skey + "; p_uin=o" + selfInfo.uin + "; uin=o" + selfInfo.uin;
  let signurl = "https://h5.qzone.qq.com/v2/vip/tx/trpc/ark-share/GenNewSignedArk?g_tk=" + Bkn + "&ark=" + encodeURIComponent(JSON.stringify(signCard));
  let signed_ark = "";
  try {
    let retData = await RequestUtil.HttpGetJson(signurl, "GET", void 0, {
      Cookie: CookieValue
    });
    signed_ark = retData.data.signed_ark;
  } catch (error) {
    logDebug("MiniApp JSON 消息生成失败", error);
  }
  return signed_ark;
}
async function SignMusicInternal(songname, singer, cover, songmid, songmusic) {
  let signurl = "https://mqq.reader.qq.com/api/mqq/share/card?accessToken&_csrfToken&source=c0003";
  let signCard = {
    app: "com.tencent.qqreader.share",
    config: {
      ctime: 1718634110,
      forward: 1,
      token: "9a63343c32d5a16bcde653eb97faa25d",
      type: "normal"
    },
    extra: {
      app_type: 1,
      appid: 100497308,
      msg_seq: 14386738075403815e3,
      uin: 1733139081
    },
    meta: {
      music: {
        action: "",
        android_pkg_name: "",
        app_type: 1,
        appid: 100497308,
        ctime: 1718634110,
        desc: singer,
        jumpUrl: "https://i.y.qq.com/v8/playsong.html?songmid=" + songmid + "&type=0",
        musicUrl: songmusic,
        preview: cover,
        cover,
        sourceMsgId: "0",
        source_icon: "https://p.qpic.cn/qqconnect/0/app_100497308_1626060999/100?max-age=2592000&t=0",
        source_url: "",
        tag: "QQ音乐",
        title: songname,
        uin: 10086
      }
    },
    prompt: "[分享]" + songname,
    ver: "0.0.0.1",
    view: "music"
  };
  let data = await RequestUtil.HttpGetJson(signurl, "POST", signCard, {
    "Cookie": "uin=o10086",
    "Content-Type": "application/json"
  });
  return data;
}
async function CreateMusicThridWay0(id = "", mid = "") {
  if (mid == "") {
    let MusicInfo = await RequestUtil.HttpGetJson('https://u.y.qq.com/cgi-bin/musicu.fcg?format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data={"comm":{"ct":24,"cv":0},"songinfo":{"method":"get_song_detail_yqq","param":{"song_type":0,"song_mid":"","song_id":' + id + '},"module":"music.pf_song_detail_svr"}}', "GET", void 0);
    mid = MusicInfo.songinfo?.data?.track_info.mid;
  }
  let MusicReal = await RequestUtil.HttpGetJson("https://api.leafone.cn/api/qqmusic?id=" + mid + "&type=8", "GET", void 0);
  return {
    ...MusicReal.data,
    mid
  };
}
async function SignMusicWrapper(id = "") {
  let MusicInfo = await CreateMusicThridWay0(id);
  let MusicCard = await SignMusicInternal(MusicInfo.name, MusicInfo.singer, MusicInfo.cover, MusicInfo.mid, "https://ws.stream.qqmusic.qq.com/" + MusicInfo.url);
  return MusicCard;
}

class NTQQSystemApi {
  static async hasOtherRunningQQProcess() {
    return napCatCore.util.hasOtherRunningQQProcess();
  }
  static async ORCImage(filePath) {
    return napCatCore.session.getNodeMiscService().wantWinScreenOCR(filePath);
  }
  static async translateEnWordToZn(words) {
    return napCatCore.session.getRichMediaService().translateEnWordToZn(words);
  }
  //调用会超时 没灯用 (好像是通知listener的) onLineDev
  static async getOnlineDev() {
    return napCatCore.session.getMsgService().getOnLineDev();
  }
  //1-2-162b9b42-65b9-4405-a8ed-2e256ec8aa50
  static async getArkJsonCollection(cid) {
    let ret = await NTEventDispatch.CallNoListenerEvent("NodeIKernelCollectionService/collectionArkShare", 5e3, "1717662698058");
    return ret;
  }
  static async BootMiniApp(appfile, params) {
    await napCatCore.session.getNodeMiscService().setMiniAppVersion("2.16.4");
    await napCatCore.session.getNodeMiscService().getMiniAppPath();
    return napCatCore.session.getNodeMiscService().startNewMiniApp(appfile, params);
  }
}

class SessionListener {
  onNTSessionCreate(args) {
  }
  onGProSessionCreate(args) {
  }
  onSessionInitComplete(args) {
  }
  onOpentelemetryInit(args) {
  }
  onUserOnlineResult(args) {
  }
  onGetSelfTinyId(args) {
  }
}

class LoginListener {
  onLoginConnected(...args) {
  }
  onLoginDisConnected(...args) {
  }
  onLoginConnecting(...args) {
  }
  onQRCodeGetPicture(arg) {
  }
  onQRCodeLoginPollingStarted(...args) {
  }
  onQRCodeSessionUserScaned(...args) {
  }
  onQRCodeLoginSucceed(arg) {
  }
  onQRCodeSessionFailed(...args) {
  }
  onLoginFailed(...args) {
  }
  onLogoutSucceed(...args) {
  }
  onLogoutFailed(...args) {
  }
  onUserLoggedIn(...args) {
  }
  onQRCodeSessionQuickLoginFailed(...args) {
  }
  onPasswordLoginFailed(...args) {
  }
  OnConfirmUnusualDeviceFailed(...args) {
  }
  onQQLoginNumLimited(...args) {
  }
  onLoginState(...args) {
  }
}

class MsgListener {
  onAddSendMsg(msgRecord) {
  }
  onBroadcastHelperDownloadComplete(broadcastHelperTransNotifyInfo) {
  }
  onBroadcastHelperProgressUpdate(broadcastHelperTransNotifyInfo) {
  }
  onChannelFreqLimitInfoUpdate(contact, z, freqLimitInfo) {
  }
  onContactUnreadCntUpdate(hashMap) {
  }
  onCustomWithdrawConfigUpdate(customWithdrawConfig) {
  }
  onDraftUpdate(contact, arrayList, j2) {
  }
  onEmojiDownloadComplete(emojiNotifyInfo) {
  }
  onEmojiResourceUpdate(emojiResourceInfo) {
  }
  onFeedEventUpdate(firstViewDirectMsgNotifyInfo) {
  }
  onFileMsgCome(arrayList) {
  }
  onFirstViewDirectMsgUpdate(firstViewDirectMsgNotifyInfo) {
  }
  onFirstViewGroupGuildMapping(arrayList) {
  }
  onGrabPasswordRedBag(i2, str, i3, recvdOrder, msgRecord) {
  }
  onGroupFileInfoAdd(groupItem) {
  }
  onGroupFileInfoUpdate(groupFileListResult) {
  }
  onGroupGuildUpdate(groupGuildNotifyInfo) {
  }
  onGroupTransferInfoAdd(groupItem) {
  }
  onGroupTransferInfoUpdate(groupFileListResult) {
  }
  onGuildInteractiveUpdate(guildInteractiveNotificationItem) {
  }
  onGuildMsgAbFlagChanged(guildMsgAbFlag) {
  }
  onGuildNotificationAbstractUpdate(guildNotificationAbstractInfo) {
  }
  onHitCsRelatedEmojiResult(downloadRelateEmojiResultInfo) {
  }
  onHitEmojiKeywordResult(hitRelatedEmojiWordsResult) {
  }
  onHitRelatedEmojiResult(relatedWordEmojiInfo) {
  }
  onImportOldDbProgressUpdate(importOldDbMsgNotifyInfo) {
  }
  onInputStatusPush(inputStatusInfo) {
  }
  onKickedOffLine(kickedInfo) {
  }
  onLineDev(arrayList) {
  }
  onLogLevelChanged(j2) {
  }
  onMsgAbstractUpdate(arrayList) {
  }
  onMsgBoxChanged(arrayList) {
  }
  onMsgDelete(contact, arrayList) {
  }
  onMsgEventListUpdate(hashMap) {
  }
  onMsgInfoListAdd(arrayList) {
  }
  onMsgInfoListUpdate(msgList) {
  }
  onMsgQRCodeStatusChanged(i2) {
  }
  onMsgRecall(i2, str, j2) {
  }
  onMsgSecurityNotify(msgRecord) {
  }
  onMsgSettingUpdate(msgSetting) {
  }
  onNtFirstViewMsgSyncEnd() {
  }
  onNtMsgSyncEnd() {
  }
  onNtMsgSyncStart() {
  }
  onReadFeedEventUpdate(firstViewDirectMsgNotifyInfo) {
  }
  onRecvGroupGuildFlag(i2) {
  }
  onRecvMsg(arrayList) {
  }
  onRecvMsgSvrRspTransInfo(j2, contact, i2, i3, str, bArr) {
  }
  onRecvOnlineFileMsg(arrayList) {
  }
  onRecvS2CMsg(arrayList) {
  }
  onRecvSysMsg(arrayList) {
  }
  onRecvUDCFlag(i2) {
  }
  onRichMediaDownloadComplete(fileTransNotifyInfo) {
  }
  onRichMediaProgerssUpdate(fileTransNotifyInfo) {
  }
  onRichMediaUploadComplete(fileTransNotifyInfo) {
  }
  onSearchGroupFileInfoUpdate(searchGroupFileResult) {
  }
  onSendMsgError(j2, contact, i2, str) {
  }
  onSysMsgNotification(i2, j2, j3, arrayList) {
  }
  onTempChatInfoUpdate(tempChatInfo) {
  }
  onUnreadCntAfterFirstView(hashMap) {
  }
  onUnreadCntUpdate(hashMap) {
  }
  onUserChannelTabStatusChanged(z) {
  }
  onUserOnlineStatusChanged(z) {
  }
  onUserTabStatusChanged(arrayList) {
  }
  onlineStatusBigIconDownloadPush(i2, j2, str) {
  }
  onlineStatusSmallIconDownloadPush(i2, j2, str) {
  }
  // 第一次发现于Linux
  onUserSecQualityChanged(...args) {
  }
  onMsgWithRichLinkInfoUpdate(...args) {
  }
  onRedTouchChanged(...args) {
  }
  // 第一次发现于Win 9.9.9-23159
  onBroadcastHelperProgerssUpdate(...args) {
  }
}

class GroupListener {
  // 发现于Win 9.9.9 23159
  onGroupMemberLevelInfoChange(...args) {
  }
  onGetGroupBulletinListResult(...args) {
  }
  onGroupAllInfoChange(...args) {
  }
  onGroupBulletinChange(...args) {
  }
  onGroupBulletinRemindNotify(...args) {
  }
  onGroupArkInviteStateResult(...args) {
  }
  onGroupBulletinRichMediaDownloadComplete(...args) {
  }
  onGroupConfMemberChange(...args) {
  }
  onGroupDetailInfoChange(...args) {
  }
  onGroupExtListUpdate(...args) {
  }
  onGroupFirstBulletinNotify(...args) {
  }
  onGroupListUpdate(updateType, groupList) {
  }
  onGroupNotifiesUpdated(dboubt, notifies) {
  }
  onGroupBulletinRichMediaProgressUpdate(...args) {
  }
  onGroupNotifiesUnreadCountUpdated(...args) {
  }
  onGroupSingleScreenNotifies(doubt, seq, notifies) {
  }
  onGroupsMsgMaskResult(...args) {
  }
  onGroupStatisticInfoChange(...args) {
  }
  onJoinGroupNotify(...args) {
  }
  onJoinGroupNoVerifyFlag(...args) {
  }
  onMemberInfoChange(groupCode, changeType, members) {
  }
  onMemberListChange(arg) {
  }
  onSearchMemberChange(...args) {
  }
  onShutUpMemberListChanged(...args) {
  }
}

class BuddyListener {
  onBuddyListChangedV2(arg) {
  }
  onAddBuddyNeedVerify(arg) {
  }
  onAddMeSettingChanged(arg) {
  }
  onAvatarUrlUpdated(arg) {
  }
  onBlockChanged(arg) {
  }
  onBuddyDetailInfoChange(arg) {
  }
  onBuddyInfoChange(arg) {
  }
  onBuddyListChange(arg) {
  }
  onBuddyRemarkUpdated(arg) {
  }
  onBuddyReqChange(arg) {
  }
  onBuddyReqUnreadCntChange(arg) {
  }
  onCheckBuddySettingResult(arg) {
  }
  onDelBatchBuddyInfos(arg) {
  }
  onDoubtBuddyReqChange(arg) {
  }
  onDoubtBuddyReqUnreadNumChange(arg) {
  }
  onNickUpdated(arg) {
  }
  onSmartInfos(arg) {
  }
  onSpacePermissionInfos(arg) {
  }
}

class ProfileListener {
  onUserDetailInfoChanged(arg) {
  }
  onProfileSimpleChanged(...args) {
  }
  onProfileDetailInfoChanged(profile) {
  }
  onStatusUpdate(...args) {
  }
  onSelfStatusChanged(...args) {
  }
  onStrangerRemarkChanged(...args) {
  }
}

var validator$2 = {};

var util$4 = {};

(function (exports) {

	const nameStartChar = ':A-Za-z_\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD';
	const nameChar = nameStartChar + '\\-.\\d\\u00B7\\u0300-\\u036F\\u203F-\\u2040';
	const nameRegexp = '[' + nameStartChar + '][' + nameChar + ']*';
	const regexName = new RegExp('^' + nameRegexp + '$');
	const getAllMatches = function (string, regex) {
	  const matches = [];
	  let match = regex.exec(string);
	  while (match) {
	    const allmatches = [];
	    allmatches.startIndex = regex.lastIndex - match[0].length;
	    const len = match.length;
	    for (let index = 0; index < len; index++) {
	      allmatches.push(match[index]);
	    }
	    matches.push(allmatches);
	    match = regex.exec(string);
	  }
	  return matches;
	};
	const isName = function (string) {
	  const match = regexName.exec(string);
	  return !(match === null || typeof match === 'undefined');
	};
	exports.isExist = function (v) {
	  return typeof v !== 'undefined';
	};
	exports.isEmptyObject = function (obj) {
	  return Object.keys(obj).length === 0;
	};

	/**
	 * Copy all the properties of a into b.
	 * @param {*} target
	 * @param {*} a
	 */
	exports.merge = function (target, a, arrayMode) {
	  if (a) {
	    const keys = Object.keys(a); // will return an array of own properties
	    const len = keys.length; //don't make it inline
	    for (let i = 0; i < len; i++) {
	      if (arrayMode === 'strict') {
	        target[keys[i]] = [a[keys[i]]];
	      } else {
	        target[keys[i]] = a[keys[i]];
	      }
	    }
	  }
	};
	/* exports.merge =function (b,a){
	  return Object.assign(b,a);
	} */

	exports.getValue = function (v) {
	  if (exports.isExist(v)) {
	    return v;
	  } else {
	    return '';
	  }
	};

	// const fakeCall = function(a) {return a;};
	// const fakeCallNoReturn = function() {};

	exports.isName = isName;
	exports.getAllMatches = getAllMatches;
	exports.nameRegexp = nameRegexp; 
} (util$4));

const util$3 = util$4;
const defaultOptions$2 = {
  allowBooleanAttributes: false,
  //A tag can have attributes without any value
  unpairedTags: []
};

//const tagsPattern = new RegExp("<\\/?([\\w:\\-_\.]+)\\s*\/?>","g");
validator$2.validate = function (xmlData, options) {
  options = Object.assign({}, defaultOptions$2, options);

  //xmlData = xmlData.replace(/(\r\n|\n|\r)/gm,"");//make it single line
  //xmlData = xmlData.replace(/(^\s*<\?xml.*?\?>)/g,"");//Remove XML starting tag
  //xmlData = xmlData.replace(/(<!DOCTYPE[\s\w\"\.\/\-\:]+(\[.*\])*\s*>)/g,"");//Remove DOCTYPE
  const tags = [];
  let tagFound = false;

  //indicates that the root tag has been closed (aka. depth 0 has been reached)
  let reachedRoot = false;
  if (xmlData[0] === '\ufeff') {
    // check for byte order mark (BOM)
    xmlData = xmlData.substr(1);
  }
  for (let i = 0; i < xmlData.length; i++) {
    if (xmlData[i] === '<' && xmlData[i + 1] === '?') {
      i += 2;
      i = readPI(xmlData, i);
      if (i.err) return i;
    } else if (xmlData[i] === '<') {
      //starting of tag
      //read until you reach to '>' avoiding any '>' in attribute value
      let tagStartPos = i;
      i++;
      if (xmlData[i] === '!') {
        i = readCommentAndCDATA(xmlData, i);
        continue;
      } else {
        let closingTag = false;
        if (xmlData[i] === '/') {
          //closing tag
          closingTag = true;
          i++;
        }
        //read tagname
        let tagName = '';
        for (; i < xmlData.length && xmlData[i] !== '>' && xmlData[i] !== ' ' && xmlData[i] !== '\t' && xmlData[i] !== '\n' && xmlData[i] !== '\r'; i++) {
          tagName += xmlData[i];
        }
        tagName = tagName.trim();
        //console.log(tagName);

        if (tagName[tagName.length - 1] === '/') {
          //self closing tag without attributes
          tagName = tagName.substring(0, tagName.length - 1);
          //continue;
          i--;
        }
        if (!validateTagName(tagName)) {
          let msg;
          if (tagName.trim().length === 0) {
            msg = "Invalid space after '<'.";
          } else {
            msg = "Tag '" + tagName + "' is an invalid name.";
          }
          return getErrorObject('InvalidTag', msg, getLineNumberForPosition(xmlData, i));
        }
        const result = readAttributeStr(xmlData, i);
        if (result === false) {
          return getErrorObject('InvalidAttr', "Attributes for '" + tagName + "' have open quote.", getLineNumberForPosition(xmlData, i));
        }
        let attrStr = result.value;
        i = result.index;
        if (attrStr[attrStr.length - 1] === '/') {
          //self closing tag
          const attrStrStart = i - attrStr.length;
          attrStr = attrStr.substring(0, attrStr.length - 1);
          const isValid = validateAttributeString(attrStr, options);
          if (isValid === true) {
            tagFound = true;
            //continue; //text may presents after self closing tag
          } else {
            //the result from the nested function returns the position of the error within the attribute
            //in order to get the 'true' error line, we need to calculate the position where the attribute begins (i - attrStr.length) and then add the position within the attribute
            //this gives us the absolute index in the entire xml, which we can use to find the line at last
            return getErrorObject(isValid.err.code, isValid.err.msg, getLineNumberForPosition(xmlData, attrStrStart + isValid.err.line));
          }
        } else if (closingTag) {
          if (!result.tagClosed) {
            return getErrorObject('InvalidTag', "Closing tag '" + tagName + "' doesn't have proper closing.", getLineNumberForPosition(xmlData, i));
          } else if (attrStr.trim().length > 0) {
            return getErrorObject('InvalidTag', "Closing tag '" + tagName + "' can't have attributes or invalid starting.", getLineNumberForPosition(xmlData, tagStartPos));
          } else if (tags.length === 0) {
            return getErrorObject('InvalidTag', "Closing tag '" + tagName + "' has not been opened.", getLineNumberForPosition(xmlData, tagStartPos));
          } else {
            const otg = tags.pop();
            if (tagName !== otg.tagName) {
              let openPos = getLineNumberForPosition(xmlData, otg.tagStartPos);
              return getErrorObject('InvalidTag', "Expected closing tag '" + otg.tagName + "' (opened in line " + openPos.line + ", col " + openPos.col + ") instead of closing tag '" + tagName + "'.", getLineNumberForPosition(xmlData, tagStartPos));
            }

            //when there are no more tags, we reached the root level.
            if (tags.length == 0) {
              reachedRoot = true;
            }
          }
        } else {
          const isValid = validateAttributeString(attrStr, options);
          if (isValid !== true) {
            //the result from the nested function returns the position of the error within the attribute
            //in order to get the 'true' error line, we need to calculate the position where the attribute begins (i - attrStr.length) and then add the position within the attribute
            //this gives us the absolute index in the entire xml, which we can use to find the line at last
            return getErrorObject(isValid.err.code, isValid.err.msg, getLineNumberForPosition(xmlData, i - attrStr.length + isValid.err.line));
          }

          //if the root level has been reached before ...
          if (reachedRoot === true) {
            return getErrorObject('InvalidXml', 'Multiple possible root nodes found.', getLineNumberForPosition(xmlData, i));
          } else if (options.unpairedTags.indexOf(tagName) !== -1) ; else {
            tags.push({
              tagName,
              tagStartPos
            });
          }
          tagFound = true;
        }

        //skip tag text value
        //It may include comments and CDATA value
        for (i++; i < xmlData.length; i++) {
          if (xmlData[i] === '<') {
            if (xmlData[i + 1] === '!') {
              //comment or CADATA
              i++;
              i = readCommentAndCDATA(xmlData, i);
              continue;
            } else if (xmlData[i + 1] === '?') {
              i = readPI(xmlData, ++i);
              if (i.err) return i;
            } else {
              break;
            }
          } else if (xmlData[i] === '&') {
            const afterAmp = validateAmpersand(xmlData, i);
            if (afterAmp == -1) return getErrorObject('InvalidChar', "char '&' is not expected.", getLineNumberForPosition(xmlData, i));
            i = afterAmp;
          } else {
            if (reachedRoot === true && !isWhiteSpace(xmlData[i])) {
              return getErrorObject('InvalidXml', "Extra text at the end", getLineNumberForPosition(xmlData, i));
            }
          }
        } //end of reading tag text value
        if (xmlData[i] === '<') {
          i--;
        }
      }
    } else {
      if (isWhiteSpace(xmlData[i])) {
        continue;
      }
      return getErrorObject('InvalidChar', "char '" + xmlData[i] + "' is not expected.", getLineNumberForPosition(xmlData, i));
    }
  }
  if (!tagFound) {
    return getErrorObject('InvalidXml', 'Start tag expected.', 1);
  } else if (tags.length == 1) {
    return getErrorObject('InvalidTag', "Unclosed tag '" + tags[0].tagName + "'.", getLineNumberForPosition(xmlData, tags[0].tagStartPos));
  } else if (tags.length > 0) {
    return getErrorObject('InvalidXml', "Invalid '" + JSON.stringify(tags.map(t => t.tagName), null, 4).replace(/\r?\n/g, '') + "' found.", {
      line: 1,
      col: 1
    });
  }
  return true;
};
function isWhiteSpace(char) {
  return char === ' ' || char === '\t' || char === '\n' || char === '\r';
}
/**
 * Read Processing insstructions and skip
 * @param {*} xmlData
 * @param {*} i
 */
function readPI(xmlData, i) {
  const start = i;
  for (; i < xmlData.length; i++) {
    if (xmlData[i] == '?' || xmlData[i] == ' ') {
      //tagname
      const tagname = xmlData.substr(start, i - start);
      if (i > 5 && tagname === 'xml') {
        return getErrorObject('InvalidXml', 'XML declaration allowed only at the start of the document.', getLineNumberForPosition(xmlData, i));
      } else if (xmlData[i] == '?' && xmlData[i + 1] == '>') {
        //check if valid attribut string
        i++;
        break;
      } else {
        continue;
      }
    }
  }
  return i;
}
function readCommentAndCDATA(xmlData, i) {
  if (xmlData.length > i + 5 && xmlData[i + 1] === '-' && xmlData[i + 2] === '-') {
    //comment
    for (i += 3; i < xmlData.length; i++) {
      if (xmlData[i] === '-' && xmlData[i + 1] === '-' && xmlData[i + 2] === '>') {
        i += 2;
        break;
      }
    }
  } else if (xmlData.length > i + 8 && xmlData[i + 1] === 'D' && xmlData[i + 2] === 'O' && xmlData[i + 3] === 'C' && xmlData[i + 4] === 'T' && xmlData[i + 5] === 'Y' && xmlData[i + 6] === 'P' && xmlData[i + 7] === 'E') {
    let angleBracketsCount = 1;
    for (i += 8; i < xmlData.length; i++) {
      if (xmlData[i] === '<') {
        angleBracketsCount++;
      } else if (xmlData[i] === '>') {
        angleBracketsCount--;
        if (angleBracketsCount === 0) {
          break;
        }
      }
    }
  } else if (xmlData.length > i + 9 && xmlData[i + 1] === '[' && xmlData[i + 2] === 'C' && xmlData[i + 3] === 'D' && xmlData[i + 4] === 'A' && xmlData[i + 5] === 'T' && xmlData[i + 6] === 'A' && xmlData[i + 7] === '[') {
    for (i += 8; i < xmlData.length; i++) {
      if (xmlData[i] === ']' && xmlData[i + 1] === ']' && xmlData[i + 2] === '>') {
        i += 2;
        break;
      }
    }
  }
  return i;
}
const doubleQuote = '"';
const singleQuote = "'";

/**
 * Keep reading xmlData until '<' is found outside the attribute value.
 * @param {string} xmlData
 * @param {number} i
 */
function readAttributeStr(xmlData, i) {
  let attrStr = '';
  let startChar = '';
  let tagClosed = false;
  for (; i < xmlData.length; i++) {
    if (xmlData[i] === doubleQuote || xmlData[i] === singleQuote) {
      if (startChar === '') {
        startChar = xmlData[i];
      } else if (startChar !== xmlData[i]) ; else {
        startChar = '';
      }
    } else if (xmlData[i] === '>') {
      if (startChar === '') {
        tagClosed = true;
        break;
      }
    }
    attrStr += xmlData[i];
  }
  if (startChar !== '') {
    return false;
  }
  return {
    value: attrStr,
    index: i,
    tagClosed: tagClosed
  };
}

/**
 * Select all the attributes whether valid or invalid.
 */
const validAttrStrRegxp = new RegExp('(\\s*)([^\\s=]+)(\\s*=)?(\\s*([\'"])(([\\s\\S])*?)\\5)?', 'g');

//attr, ="sd", a="amit's", a="sd"b="saf", ab  cd=""

function validateAttributeString(attrStr, options) {
  //console.log("start:"+attrStr+":end");

  //if(attrStr.trim().length === 0) return true; //empty string

  const matches = util$3.getAllMatches(attrStr, validAttrStrRegxp);
  const attrNames = {};
  for (let i = 0; i < matches.length; i++) {
    if (matches[i][1].length === 0) {
      //nospace before attribute name: a="sd"b="saf"
      return getErrorObject('InvalidAttr', "Attribute '" + matches[i][2] + "' has no space in starting.", getPositionFromMatch(matches[i]));
    } else if (matches[i][3] !== undefined && matches[i][4] === undefined) {
      return getErrorObject('InvalidAttr', "Attribute '" + matches[i][2] + "' is without value.", getPositionFromMatch(matches[i]));
    } else if (matches[i][3] === undefined && !options.allowBooleanAttributes) {
      //independent attribute: ab
      return getErrorObject('InvalidAttr', "boolean attribute '" + matches[i][2] + "' is not allowed.", getPositionFromMatch(matches[i]));
    }
    /* else if(matches[i][6] === undefined){//attribute without value: ab=
                    return { err: { code:"InvalidAttr",msg:"attribute " + matches[i][2] + " has no value assigned."}};
                } */
    const attrName = matches[i][2];
    if (!validateAttrName(attrName)) {
      return getErrorObject('InvalidAttr', "Attribute '" + attrName + "' is an invalid name.", getPositionFromMatch(matches[i]));
    }
    if (!attrNames.hasOwnProperty(attrName)) {
      //check for duplicate attribute.
      attrNames[attrName] = 1;
    } else {
      return getErrorObject('InvalidAttr', "Attribute '" + attrName + "' is repeated.", getPositionFromMatch(matches[i]));
    }
  }
  return true;
}
function validateNumberAmpersand(xmlData, i) {
  let re = /\d/;
  if (xmlData[i] === 'x') {
    i++;
    re = /[\da-fA-F]/;
  }
  for (; i < xmlData.length; i++) {
    if (xmlData[i] === ';') return i;
    if (!xmlData[i].match(re)) break;
  }
  return -1;
}
function validateAmpersand(xmlData, i) {
  // https://www.w3.org/TR/xml/#dt-charref
  i++;
  if (xmlData[i] === ';') return -1;
  if (xmlData[i] === '#') {
    i++;
    return validateNumberAmpersand(xmlData, i);
  }
  let count = 0;
  for (; i < xmlData.length; i++, count++) {
    if (xmlData[i].match(/\w/) && count < 20) continue;
    if (xmlData[i] === ';') break;
    return -1;
  }
  return i;
}
function getErrorObject(code, message, lineNumber) {
  return {
    err: {
      code: code,
      msg: message,
      line: lineNumber.line || lineNumber,
      col: lineNumber.col
    }
  };
}
function validateAttrName(attrName) {
  return util$3.isName(attrName);
}

// const startsWithXML = /^xml/i;

function validateTagName(tagname) {
  return util$3.isName(tagname) /* && !tagname.match(startsWithXML) */;
}

//this function returns the line number for the character at the given index
function getLineNumberForPosition(xmlData, index) {
  const lines = xmlData.substring(0, index).split(/\r?\n/);
  return {
    line: lines.length,
    // column number is last line's length + 1, because column numbering starts at 1:
    col: lines[lines.length - 1].length + 1
  };
}

//this function returns the position of the first character of match within attrStr
function getPositionFromMatch(match) {
  return match.startIndex + match[1].length;
}

var OptionsBuilder = {};

const defaultOptions$1 = {
  preserveOrder: false,
  attributeNamePrefix: '@_',
  attributesGroupName: false,
  textNodeName: '#text',
  ignoreAttributes: true,
  removeNSPrefix: false,
  // remove NS from tag name or attribute name if true
  allowBooleanAttributes: false,
  //a tag can have attributes without any value
  //ignoreRootElement : false,
  parseTagValue: true,
  parseAttributeValue: false,
  trimValues: true,
  //Trim string values of tag and attributes
  cdataPropName: false,
  numberParseOptions: {
    hex: true,
    leadingZeros: true,
    eNotation: true
  },
  tagValueProcessor: function (tagName, val) {
    return val;
  },
  attributeValueProcessor: function (attrName, val) {
    return val;
  },
  stopNodes: [],
  //nested tags will not be parsed even for errors
  alwaysCreateTextNode: false,
  isArray: () => false,
  commentPropName: false,
  unpairedTags: [],
  processEntities: true,
  htmlEntities: false,
  ignoreDeclaration: false,
  ignorePiTags: false,
  transformTagName: false,
  transformAttributeName: false,
  updateTag: function (tagName, jPath, attrs) {
    return tagName;
  }
  // skipEmptyListItem: false
};
const buildOptions$1 = function (options) {
  return Object.assign({}, defaultOptions$1, options);
};
OptionsBuilder.buildOptions = buildOptions$1;
OptionsBuilder.defaultOptions = defaultOptions$1;

class XmlNode {
  constructor(tagname) {
    this.tagname = tagname;
    this.child = []; //nested tags, text, cdata, comments in order
    this[":@"] = {}; //attributes map
  }
  add(key, val) {
    // this.child.push( {name : key, val: val, isCdata: isCdata });
    if (key === "__proto__") key = "#__proto__";
    this.child.push({
      [key]: val
    });
  }
  addChild(node) {
    if (node.tagname === "__proto__") node.tagname = "#__proto__";
    if (node[":@"] && Object.keys(node[":@"]).length > 0) {
      this.child.push({
        [node.tagname]: node.child,
        [":@"]: node[":@"]
      });
    } else {
      this.child.push({
        [node.tagname]: node.child
      });
    }
  }
}
var xmlNode$1 = XmlNode;

const util$2 = util$4;

//TODO: handle comments
function readDocType$1(xmlData, i) {
  const entities = {};
  if (xmlData[i + 3] === 'O' && xmlData[i + 4] === 'C' && xmlData[i + 5] === 'T' && xmlData[i + 6] === 'Y' && xmlData[i + 7] === 'P' && xmlData[i + 8] === 'E') {
    i = i + 9;
    let angleBracketsCount = 1;
    let hasBody = false,
      comment = false;
    let exp = "";
    for (; i < xmlData.length; i++) {
      if (xmlData[i] === '<' && !comment) {
        //Determine the tag type
        if (hasBody && isEntity(xmlData, i)) {
          i += 7;
          [entityName, val, i] = readEntityExp(xmlData, i + 1);
          if (val.indexOf("&") === -1)
            //Parameter entities are not supported
            entities[validateEntityName(entityName)] = {
              regx: RegExp(`&${entityName};`, "g"),
              val: val
            };
        } else if (hasBody && isElement(xmlData, i)) i += 8; //Not supported
        else if (hasBody && isAttlist(xmlData, i)) i += 8; //Not supported
        else if (hasBody && isNotation(xmlData, i)) i += 9; //Not supported
        else if (isComment) comment = true;else throw new Error("Invalid DOCTYPE");
        angleBracketsCount++;
        exp = "";
      } else if (xmlData[i] === '>') {
        //Read tag content
        if (comment) {
          if (xmlData[i - 1] === "-" && xmlData[i - 2] === "-") {
            comment = false;
            angleBracketsCount--;
          }
        } else {
          angleBracketsCount--;
        }
        if (angleBracketsCount === 0) {
          break;
        }
      } else if (xmlData[i] === '[') {
        hasBody = true;
      } else {
        exp += xmlData[i];
      }
    }
    if (angleBracketsCount !== 0) {
      throw new Error(`Unclosed DOCTYPE`);
    }
  } else {
    throw new Error(`Invalid Tag instead of DOCTYPE`);
  }
  return {
    entities,
    i
  };
}
function readEntityExp(xmlData, i) {
  //External entities are not supported
  //    <!ENTITY ext SYSTEM "http://normal-website.com" >

  //Parameter entities are not supported
  //    <!ENTITY entityname "&anotherElement;">

  //Internal entities are supported
  //    <!ENTITY entityname "replacement text">

  //read EntityName
  let entityName = "";
  for (; i < xmlData.length && xmlData[i] !== "'" && xmlData[i] !== '"'; i++) {
    // if(xmlData[i] === " ") continue;
    // else 
    entityName += xmlData[i];
  }
  entityName = entityName.trim();
  if (entityName.indexOf(" ") !== -1) throw new Error("External entites are not supported");

  //read Entity Value
  const startChar = xmlData[i++];
  let val = "";
  for (; i < xmlData.length && xmlData[i] !== startChar; i++) {
    val += xmlData[i];
  }
  return [entityName, val, i];
}
function isComment(xmlData, i) {
  if (xmlData[i + 1] === '!' && xmlData[i + 2] === '-' && xmlData[i + 3] === '-') return true;
  return false;
}
function isEntity(xmlData, i) {
  if (xmlData[i + 1] === '!' && xmlData[i + 2] === 'E' && xmlData[i + 3] === 'N' && xmlData[i + 4] === 'T' && xmlData[i + 5] === 'I' && xmlData[i + 6] === 'T' && xmlData[i + 7] === 'Y') return true;
  return false;
}
function isElement(xmlData, i) {
  if (xmlData[i + 1] === '!' && xmlData[i + 2] === 'E' && xmlData[i + 3] === 'L' && xmlData[i + 4] === 'E' && xmlData[i + 5] === 'M' && xmlData[i + 6] === 'E' && xmlData[i + 7] === 'N' && xmlData[i + 8] === 'T') return true;
  return false;
}
function isAttlist(xmlData, i) {
  if (xmlData[i + 1] === '!' && xmlData[i + 2] === 'A' && xmlData[i + 3] === 'T' && xmlData[i + 4] === 'T' && xmlData[i + 5] === 'L' && xmlData[i + 6] === 'I' && xmlData[i + 7] === 'S' && xmlData[i + 8] === 'T') return true;
  return false;
}
function isNotation(xmlData, i) {
  if (xmlData[i + 1] === '!' && xmlData[i + 2] === 'N' && xmlData[i + 3] === 'O' && xmlData[i + 4] === 'T' && xmlData[i + 5] === 'A' && xmlData[i + 6] === 'T' && xmlData[i + 7] === 'I' && xmlData[i + 8] === 'O' && xmlData[i + 9] === 'N') return true;
  return false;
}
function validateEntityName(name) {
  if (util$2.isName(name)) return name;else throw new Error(`Invalid entity name ${name}`);
}
var DocTypeReader = readDocType$1;

const hexRegex = /^[-+]?0x[a-fA-F0-9]+$/;
const numRegex = /^([\-\+])?(0*)(\.[0-9]+([eE]\-?[0-9]+)?|[0-9]+(\.[0-9]+([eE]\-?[0-9]+)?)?)$/;
// const octRegex = /0x[a-z0-9]+/;
// const binRegex = /0x[a-z0-9]+/;

//polyfill
if (!Number.parseInt && window.parseInt) {
  Number.parseInt = window.parseInt;
}
if (!Number.parseFloat && window.parseFloat) {
  Number.parseFloat = window.parseFloat;
}
const consider = {
  hex: true,
  leadingZeros: true,
  decimalPoint: "\.",
  eNotation: true
  //skipLike: /regex/
};
function toNumber$1(str, options = {}) {
  // const options = Object.assign({}, consider);
  // if(opt.leadingZeros === false){
  //     options.leadingZeros = false;
  // }else if(opt.hex === false){
  //     options.hex = false;
  // }

  options = Object.assign({}, consider, options);
  if (!str || typeof str !== "string") return str;
  let trimmedStr = str.trim();
  // if(trimmedStr === "0.0") return 0;
  // else if(trimmedStr === "+0.0") return 0;
  // else if(trimmedStr === "-0.0") return -0;

  if (options.skipLike !== undefined && options.skipLike.test(trimmedStr)) return str;else if (options.hex && hexRegex.test(trimmedStr)) {
    return Number.parseInt(trimmedStr, 16);
    // } else if (options.parseOct && octRegex.test(str)) {
    //     return Number.parseInt(val, 8);
    // }else if (options.parseBin && binRegex.test(str)) {
    //     return Number.parseInt(val, 2);
  } else {
    //separate negative sign, leading zeros, and rest number
    const match = numRegex.exec(trimmedStr);
    if (match) {
      const sign = match[1];
      const leadingZeros = match[2];
      let numTrimmedByZeros = trimZeros(match[3]); //complete num without leading zeros
      //trim ending zeros for floating number

      const eNotation = match[4] || match[6];
      if (!options.leadingZeros && leadingZeros.length > 0 && sign && trimmedStr[2] !== ".") return str; //-0123
      else if (!options.leadingZeros && leadingZeros.length > 0 && !sign && trimmedStr[1] !== ".") return str; //0123
      else {
        //no leading zeros or leading zeros are allowed
        const num = Number(trimmedStr);
        const numStr = "" + num;
        if (numStr.search(/[eE]/) !== -1) {
          //given number is long and parsed to eNotation
          if (options.eNotation) return num;else return str;
        } else if (eNotation) {
          //given number has enotation
          if (options.eNotation) return num;else return str;
        } else if (trimmedStr.indexOf(".") !== -1) {
          //floating number
          // const decimalPart = match[5].substr(1);
          // const intPart = trimmedStr.substr(0,trimmedStr.indexOf("."));

          // const p = numStr.indexOf(".");
          // const givenIntPart = numStr.substr(0,p);
          // const givenDecPart = numStr.substr(p+1);
          if (numStr === "0" && numTrimmedByZeros === "") return num; //0.0
          else if (numStr === numTrimmedByZeros) return num; //0.456. 0.79000
          else if (sign && numStr === "-" + numTrimmedByZeros) return num;else return str;
        }
        if (leadingZeros) {
          // if(numTrimmedByZeros === numStr){
          //     if(options.leadingZeros) return num;
          //     else return str;
          // }else return str;
          if (numTrimmedByZeros === numStr) return num;else if (sign + numTrimmedByZeros === numStr) return num;else return str;
        }
        if (trimmedStr === numStr) return num;else if (trimmedStr === sign + numStr) return num;
        // else{
        //     //number with +/- sign
        //     trimmedStr.test(/[-+][0-9]);

        // }
        return str;
      }
      // else if(!eNotation && trimmedStr && trimmedStr !== Number(trimmedStr) ) return str;
    } else {
      //non-numeric string
      return str;
    }
  }
}

/**
 * 
 * @param {string} numStr without leading zeros
 * @returns 
 */
function trimZeros(numStr) {
  if (numStr && numStr.indexOf(".") !== -1) {
    //float
    numStr = numStr.replace(/0+$/, ""); //remove ending zeros
    if (numStr === ".") numStr = "0";else if (numStr[0] === ".") numStr = "0" + numStr;else if (numStr[numStr.length - 1] === ".") numStr = numStr.substr(0, numStr.length - 1);
    return numStr;
  }
  return numStr;
}
var strnum = toNumber$1;

///@ts-check
const util$1 = util$4;
const xmlNode = xmlNode$1;
const readDocType = DocTypeReader;
const toNumber = strnum;

// const regx =
//   '<((!\\[CDATA\\[([\\s\\S]*?)(]]>))|((NAME:)?(NAME))([^>]*)>|((\\/)(NAME)\\s*>))([^<]*)'
//   .replace(/NAME/g, util.nameRegexp);

//const tagsRegx = new RegExp("<(\\/?[\\w:\\-\._]+)([^>]*)>(\\s*"+cdataRegx+")*([^<]+)?","g");
//const tagsRegx = new RegExp("<(\\/?)((\\w*:)?([\\w:\\-\._]+))([^>]*)>([^<]*)("+cdataRegx+"([^<]*))*([^<]+)?","g");

let OrderedObjParser$1 = class OrderedObjParser {
  constructor(options) {
    this.options = options;
    this.currentNode = null;
    this.tagsNodeStack = [];
    this.docTypeEntities = {};
    this.lastEntities = {
      "apos": {
        regex: /&(apos|#39|#x27);/g,
        val: "'"
      },
      "gt": {
        regex: /&(gt|#62|#x3E);/g,
        val: ">"
      },
      "lt": {
        regex: /&(lt|#60|#x3C);/g,
        val: "<"
      },
      "quot": {
        regex: /&(quot|#34|#x22);/g,
        val: "\""
      }
    };
    this.ampEntity = {
      regex: /&(amp|#38|#x26);/g,
      val: "&"
    };
    this.htmlEntities = {
      "space": {
        regex: /&(nbsp|#160);/g,
        val: " "
      },
      // "lt" : { regex: /&(lt|#60);/g, val: "<" },
      // "gt" : { regex: /&(gt|#62);/g, val: ">" },
      // "amp" : { regex: /&(amp|#38);/g, val: "&" },
      // "quot" : { regex: /&(quot|#34);/g, val: "\"" },
      // "apos" : { regex: /&(apos|#39);/g, val: "'" },
      "cent": {
        regex: /&(cent|#162);/g,
        val: "¢"
      },
      "pound": {
        regex: /&(pound|#163);/g,
        val: "£"
      },
      "yen": {
        regex: /&(yen|#165);/g,
        val: "¥"
      },
      "euro": {
        regex: /&(euro|#8364);/g,
        val: "€"
      },
      "copyright": {
        regex: /&(copy|#169);/g,
        val: "©"
      },
      "reg": {
        regex: /&(reg|#174);/g,
        val: "®"
      },
      "inr": {
        regex: /&(inr|#8377);/g,
        val: "₹"
      },
      "num_dec": {
        regex: /&#([0-9]{1,7});/g,
        val: (_, str) => String.fromCharCode(Number.parseInt(str, 10))
      },
      "num_hex": {
        regex: /&#x([0-9a-fA-F]{1,6});/g,
        val: (_, str) => String.fromCharCode(Number.parseInt(str, 16))
      }
    };
    this.addExternalEntities = addExternalEntities;
    this.parseXml = parseXml;
    this.parseTextData = parseTextData;
    this.resolveNameSpace = resolveNameSpace;
    this.buildAttributesMap = buildAttributesMap;
    this.isItStopNode = isItStopNode;
    this.replaceEntitiesValue = replaceEntitiesValue$1;
    this.readStopNodeData = readStopNodeData;
    this.saveTextToParentTag = saveTextToParentTag;
    this.addChild = addChild;
  }
};
function addExternalEntities(externalEntities) {
  const entKeys = Object.keys(externalEntities);
  for (let i = 0; i < entKeys.length; i++) {
    const ent = entKeys[i];
    this.lastEntities[ent] = {
      regex: new RegExp("&" + ent + ";", "g"),
      val: externalEntities[ent]
    };
  }
}

/**
 * @param {string} val
 * @param {string} tagName
 * @param {string} jPath
 * @param {boolean} dontTrim
 * @param {boolean} hasAttributes
 * @param {boolean} isLeafNode
 * @param {boolean} escapeEntities
 */
function parseTextData(val, tagName, jPath, dontTrim, hasAttributes, isLeafNode, escapeEntities) {
  if (val !== undefined) {
    if (this.options.trimValues && !dontTrim) {
      val = val.trim();
    }
    if (val.length > 0) {
      if (!escapeEntities) val = this.replaceEntitiesValue(val);
      const newval = this.options.tagValueProcessor(tagName, val, jPath, hasAttributes, isLeafNode);
      if (newval === null || newval === undefined) {
        //don't parse
        return val;
      } else if (typeof newval !== typeof val || newval !== val) {
        //overwrite
        return newval;
      } else if (this.options.trimValues) {
        return parseValue(val, this.options.parseTagValue, this.options.numberParseOptions);
      } else {
        const trimmedVal = val.trim();
        if (trimmedVal === val) {
          return parseValue(val, this.options.parseTagValue, this.options.numberParseOptions);
        } else {
          return val;
        }
      }
    }
  }
}
function resolveNameSpace(tagname) {
  if (this.options.removeNSPrefix) {
    const tags = tagname.split(':');
    const prefix = tagname.charAt(0) === '/' ? '/' : '';
    if (tags[0] === 'xmlns') {
      return '';
    }
    if (tags.length === 2) {
      tagname = prefix + tags[1];
    }
  }
  return tagname;
}

//TODO: change regex to capture NS
//const attrsRegx = new RegExp("([\\w\\-\\.\\:]+)\\s*=\\s*(['\"])((.|\n)*?)\\2","gm");
const attrsRegx = new RegExp('([^\\s=]+)\\s*(=\\s*([\'"])([\\s\\S]*?)\\3)?', 'gm');
function buildAttributesMap(attrStr, jPath, tagName) {
  if (!this.options.ignoreAttributes && typeof attrStr === 'string') {
    // attrStr = attrStr.replace(/\r?\n/g, ' ');
    //attrStr = attrStr || attrStr.trim();

    const matches = util$1.getAllMatches(attrStr, attrsRegx);
    const len = matches.length; //don't make it inline
    const attrs = {};
    for (let i = 0; i < len; i++) {
      const attrName = this.resolveNameSpace(matches[i][1]);
      let oldVal = matches[i][4];
      let aName = this.options.attributeNamePrefix + attrName;
      if (attrName.length) {
        if (this.options.transformAttributeName) {
          aName = this.options.transformAttributeName(aName);
        }
        if (aName === "__proto__") aName = "#__proto__";
        if (oldVal !== undefined) {
          if (this.options.trimValues) {
            oldVal = oldVal.trim();
          }
          oldVal = this.replaceEntitiesValue(oldVal);
          const newVal = this.options.attributeValueProcessor(attrName, oldVal, jPath);
          if (newVal === null || newVal === undefined) {
            //don't parse
            attrs[aName] = oldVal;
          } else if (typeof newVal !== typeof oldVal || newVal !== oldVal) {
            //overwrite
            attrs[aName] = newVal;
          } else {
            //parse
            attrs[aName] = parseValue(oldVal, this.options.parseAttributeValue, this.options.numberParseOptions);
          }
        } else if (this.options.allowBooleanAttributes) {
          attrs[aName] = true;
        }
      }
    }
    if (!Object.keys(attrs).length) {
      return;
    }
    if (this.options.attributesGroupName) {
      const attrCollection = {};
      attrCollection[this.options.attributesGroupName] = attrs;
      return attrCollection;
    }
    return attrs;
  }
}
const parseXml = function (xmlData) {
  xmlData = xmlData.replace(/\r\n?/g, "\n"); //TODO: remove this line
  const xmlObj = new xmlNode('!xml');
  let currentNode = xmlObj;
  let textData = "";
  let jPath = "";
  for (let i = 0; i < xmlData.length; i++) {
    //for each char in XML data
    const ch = xmlData[i];
    if (ch === '<') {
      // const nextIndex = i+1;
      // const _2ndChar = xmlData[nextIndex];
      if (xmlData[i + 1] === '/') {
        //Closing Tag
        const closeIndex = findClosingIndex(xmlData, ">", i, "Closing Tag is not closed.");
        let tagName = xmlData.substring(i + 2, closeIndex).trim();
        if (this.options.removeNSPrefix) {
          const colonIndex = tagName.indexOf(":");
          if (colonIndex !== -1) {
            tagName = tagName.substr(colonIndex + 1);
          }
        }
        if (this.options.transformTagName) {
          tagName = this.options.transformTagName(tagName);
        }
        if (currentNode) {
          textData = this.saveTextToParentTag(textData, currentNode, jPath);
        }

        //check if last tag of nested tag was unpaired tag
        const lastTagName = jPath.substring(jPath.lastIndexOf(".") + 1);
        if (tagName && this.options.unpairedTags.indexOf(tagName) !== -1) {
          throw new Error(`Unpaired tag can not be used as closing tag: </${tagName}>`);
        }
        let propIndex = 0;
        if (lastTagName && this.options.unpairedTags.indexOf(lastTagName) !== -1) {
          propIndex = jPath.lastIndexOf('.', jPath.lastIndexOf('.') - 1);
          this.tagsNodeStack.pop();
        } else {
          propIndex = jPath.lastIndexOf(".");
        }
        jPath = jPath.substring(0, propIndex);
        currentNode = this.tagsNodeStack.pop(); //avoid recursion, set the parent tag scope
        textData = "";
        i = closeIndex;
      } else if (xmlData[i + 1] === '?') {
        let tagData = readTagExp(xmlData, i, false, "?>");
        if (!tagData) throw new Error("Pi Tag is not closed.");
        textData = this.saveTextToParentTag(textData, currentNode, jPath);
        if (this.options.ignoreDeclaration && tagData.tagName === "?xml" || this.options.ignorePiTags) ; else {
          const childNode = new xmlNode(tagData.tagName);
          childNode.add(this.options.textNodeName, "");
          if (tagData.tagName !== tagData.tagExp && tagData.attrExpPresent) {
            childNode[":@"] = this.buildAttributesMap(tagData.tagExp, jPath, tagData.tagName);
          }
          this.addChild(currentNode, childNode, jPath);
        }
        i = tagData.closeIndex + 1;
      } else if (xmlData.substr(i + 1, 3) === '!--') {
        const endIndex = findClosingIndex(xmlData, "-->", i + 4, "Comment is not closed.");
        if (this.options.commentPropName) {
          const comment = xmlData.substring(i + 4, endIndex - 2);
          textData = this.saveTextToParentTag(textData, currentNode, jPath);
          currentNode.add(this.options.commentPropName, [{
            [this.options.textNodeName]: comment
          }]);
        }
        i = endIndex;
      } else if (xmlData.substr(i + 1, 2) === '!D') {
        const result = readDocType(xmlData, i);
        this.docTypeEntities = result.entities;
        i = result.i;
      } else if (xmlData.substr(i + 1, 2) === '![') {
        const closeIndex = findClosingIndex(xmlData, "]]>", i, "CDATA is not closed.") - 2;
        const tagExp = xmlData.substring(i + 9, closeIndex);
        textData = this.saveTextToParentTag(textData, currentNode, jPath);
        let val = this.parseTextData(tagExp, currentNode.tagname, jPath, true, false, true, true);
        if (val == undefined) val = "";

        //cdata should be set even if it is 0 length string
        if (this.options.cdataPropName) {
          currentNode.add(this.options.cdataPropName, [{
            [this.options.textNodeName]: tagExp
          }]);
        } else {
          currentNode.add(this.options.textNodeName, val);
        }
        i = closeIndex + 2;
      } else {
        //Opening tag
        let result = readTagExp(xmlData, i, this.options.removeNSPrefix);
        let tagName = result.tagName;
        const rawTagName = result.rawTagName;
        let tagExp = result.tagExp;
        let attrExpPresent = result.attrExpPresent;
        let closeIndex = result.closeIndex;
        if (this.options.transformTagName) {
          tagName = this.options.transformTagName(tagName);
        }

        //save text as child node
        if (currentNode && textData) {
          if (currentNode.tagname !== '!xml') {
            //when nested tag is found
            textData = this.saveTextToParentTag(textData, currentNode, jPath, false);
          }
        }

        //check if last tag was unpaired tag
        const lastTag = currentNode;
        if (lastTag && this.options.unpairedTags.indexOf(lastTag.tagname) !== -1) {
          currentNode = this.tagsNodeStack.pop();
          jPath = jPath.substring(0, jPath.lastIndexOf("."));
        }
        if (tagName !== xmlObj.tagname) {
          jPath += jPath ? "." + tagName : tagName;
        }
        if (this.isItStopNode(this.options.stopNodes, jPath, tagName)) {
          let tagContent = "";
          //self-closing tag
          if (tagExp.length > 0 && tagExp.lastIndexOf("/") === tagExp.length - 1) {
            if (tagName[tagName.length - 1] === "/") {
              //remove trailing '/'
              tagName = tagName.substr(0, tagName.length - 1);
              jPath = jPath.substr(0, jPath.length - 1);
              tagExp = tagName;
            } else {
              tagExp = tagExp.substr(0, tagExp.length - 1);
            }
            i = result.closeIndex;
          }
          //unpaired tag
          else if (this.options.unpairedTags.indexOf(tagName) !== -1) {
            i = result.closeIndex;
          }
          //normal tag
          else {
            //read until closing tag is found
            const result = this.readStopNodeData(xmlData, rawTagName, closeIndex + 1);
            if (!result) throw new Error(`Unexpected end of ${rawTagName}`);
            i = result.i;
            tagContent = result.tagContent;
          }
          const childNode = new xmlNode(tagName);
          if (tagName !== tagExp && attrExpPresent) {
            childNode[":@"] = this.buildAttributesMap(tagExp, jPath, tagName);
          }
          if (tagContent) {
            tagContent = this.parseTextData(tagContent, tagName, jPath, true, attrExpPresent, true, true);
          }
          jPath = jPath.substr(0, jPath.lastIndexOf("."));
          childNode.add(this.options.textNodeName, tagContent);
          this.addChild(currentNode, childNode, jPath);
        } else {
          //selfClosing tag
          if (tagExp.length > 0 && tagExp.lastIndexOf("/") === tagExp.length - 1) {
            if (tagName[tagName.length - 1] === "/") {
              //remove trailing '/'
              tagName = tagName.substr(0, tagName.length - 1);
              jPath = jPath.substr(0, jPath.length - 1);
              tagExp = tagName;
            } else {
              tagExp = tagExp.substr(0, tagExp.length - 1);
            }
            if (this.options.transformTagName) {
              tagName = this.options.transformTagName(tagName);
            }
            const childNode = new xmlNode(tagName);
            if (tagName !== tagExp && attrExpPresent) {
              childNode[":@"] = this.buildAttributesMap(tagExp, jPath, tagName);
            }
            this.addChild(currentNode, childNode, jPath);
            jPath = jPath.substr(0, jPath.lastIndexOf("."));
          }
          //opening tag
          else {
            const childNode = new xmlNode(tagName);
            this.tagsNodeStack.push(currentNode);
            if (tagName !== tagExp && attrExpPresent) {
              childNode[":@"] = this.buildAttributesMap(tagExp, jPath, tagName);
            }
            this.addChild(currentNode, childNode, jPath);
            currentNode = childNode;
          }
          textData = "";
          i = closeIndex;
        }
      }
    } else {
      textData += xmlData[i];
    }
  }
  return xmlObj.child;
};
function addChild(currentNode, childNode, jPath) {
  const result = this.options.updateTag(childNode.tagname, jPath, childNode[":@"]);
  if (result === false) ; else if (typeof result === "string") {
    childNode.tagname = result;
    currentNode.addChild(childNode);
  } else {
    currentNode.addChild(childNode);
  }
}
const replaceEntitiesValue$1 = function (val) {
  if (this.options.processEntities) {
    for (let entityName in this.docTypeEntities) {
      const entity = this.docTypeEntities[entityName];
      val = val.replace(entity.regx, entity.val);
    }
    for (let entityName in this.lastEntities) {
      const entity = this.lastEntities[entityName];
      val = val.replace(entity.regex, entity.val);
    }
    if (this.options.htmlEntities) {
      for (let entityName in this.htmlEntities) {
        const entity = this.htmlEntities[entityName];
        val = val.replace(entity.regex, entity.val);
      }
    }
    val = val.replace(this.ampEntity.regex, this.ampEntity.val);
  }
  return val;
};
function saveTextToParentTag(textData, currentNode, jPath, isLeafNode) {
  if (textData) {
    //store previously collected data as textNode
    if (isLeafNode === undefined) isLeafNode = Object.keys(currentNode.child).length === 0;
    textData = this.parseTextData(textData, currentNode.tagname, jPath, false, currentNode[":@"] ? Object.keys(currentNode[":@"]).length !== 0 : false, isLeafNode);
    if (textData !== undefined && textData !== "") currentNode.add(this.options.textNodeName, textData);
    textData = "";
  }
  return textData;
}

//TODO: use jPath to simplify the logic
/**
 * 
 * @param {string[]} stopNodes 
 * @param {string} jPath
 * @param {string} currentTagName 
 */
function isItStopNode(stopNodes, jPath, currentTagName) {
  const allNodesExp = "*." + currentTagName;
  for (const stopNodePath in stopNodes) {
    const stopNodeExp = stopNodes[stopNodePath];
    if (allNodesExp === stopNodeExp || jPath === stopNodeExp) return true;
  }
  return false;
}

/**
 * Returns the tag Expression and where it is ending handling single-double quotes situation
 * @param {string} xmlData 
 * @param {number} i starting index
 * @returns 
 */
function tagExpWithClosingIndex(xmlData, i, closingChar = ">") {
  let attrBoundary;
  let tagExp = "";
  for (let index = i; index < xmlData.length; index++) {
    let ch = xmlData[index];
    if (attrBoundary) {
      if (ch === attrBoundary) attrBoundary = ""; //reset
    } else if (ch === '"' || ch === "'") {
      attrBoundary = ch;
    } else if (ch === closingChar[0]) {
      if (closingChar[1]) {
        if (xmlData[index + 1] === closingChar[1]) {
          return {
            data: tagExp,
            index: index
          };
        }
      } else {
        return {
          data: tagExp,
          index: index
        };
      }
    } else if (ch === '\t') {
      ch = " ";
    }
    tagExp += ch;
  }
}
function findClosingIndex(xmlData, str, i, errMsg) {
  const closingIndex = xmlData.indexOf(str, i);
  if (closingIndex === -1) {
    throw new Error(errMsg);
  } else {
    return closingIndex + str.length - 1;
  }
}
function readTagExp(xmlData, i, removeNSPrefix, closingChar = ">") {
  const result = tagExpWithClosingIndex(xmlData, i + 1, closingChar);
  if (!result) return;
  let tagExp = result.data;
  const closeIndex = result.index;
  const separatorIndex = tagExp.search(/\s/);
  let tagName = tagExp;
  let attrExpPresent = true;
  if (separatorIndex !== -1) {
    //separate tag name and attributes expression
    tagName = tagExp.substring(0, separatorIndex);
    tagExp = tagExp.substring(separatorIndex + 1).trimStart();
  }
  const rawTagName = tagName;
  if (removeNSPrefix) {
    const colonIndex = tagName.indexOf(":");
    if (colonIndex !== -1) {
      tagName = tagName.substr(colonIndex + 1);
      attrExpPresent = tagName !== result.data.substr(colonIndex + 1);
    }
  }
  return {
    tagName: tagName,
    tagExp: tagExp,
    closeIndex: closeIndex,
    attrExpPresent: attrExpPresent,
    rawTagName: rawTagName
  };
}
/**
 * find paired tag for a stop node
 * @param {string} xmlData 
 * @param {string} tagName 
 * @param {number} i 
 */
function readStopNodeData(xmlData, tagName, i) {
  const startIndex = i;
  // Starting at 1 since we already have an open tag
  let openTagCount = 1;
  for (; i < xmlData.length; i++) {
    if (xmlData[i] === "<") {
      if (xmlData[i + 1] === "/") {
        //close tag
        const closeIndex = findClosingIndex(xmlData, ">", i, `${tagName} is not closed`);
        let closeTagName = xmlData.substring(i + 2, closeIndex).trim();
        if (closeTagName === tagName) {
          openTagCount--;
          if (openTagCount === 0) {
            return {
              tagContent: xmlData.substring(startIndex, i),
              i: closeIndex
            };
          }
        }
        i = closeIndex;
      } else if (xmlData[i + 1] === '?') {
        const closeIndex = findClosingIndex(xmlData, "?>", i + 1, "StopNode is not closed.");
        i = closeIndex;
      } else if (xmlData.substr(i + 1, 3) === '!--') {
        const closeIndex = findClosingIndex(xmlData, "-->", i + 3, "StopNode is not closed.");
        i = closeIndex;
      } else if (xmlData.substr(i + 1, 2) === '![') {
        const closeIndex = findClosingIndex(xmlData, "]]>", i, "StopNode is not closed.") - 2;
        i = closeIndex;
      } else {
        const tagData = readTagExp(xmlData, i, '>');
        if (tagData) {
          const openTagName = tagData && tagData.tagName;
          if (openTagName === tagName && tagData.tagExp[tagData.tagExp.length - 1] !== "/") {
            openTagCount++;
          }
          i = tagData.closeIndex;
        }
      }
    }
  } //end for loop
}
function parseValue(val, shouldParse, options) {
  if (shouldParse && typeof val === 'string') {
    //console.log(options)
    const newval = val.trim();
    if (newval === 'true') return true;else if (newval === 'false') return false;else return toNumber(val, options);
  } else {
    if (util$1.isExist(val)) {
      return val;
    } else {
      return '';
    }
  }
}
var OrderedObjParser_1 = OrderedObjParser$1;

var node2json = {};

/**
 * 
 * @param {array} node 
 * @param {any} options 
 * @returns 
 */
function prettify$1(node, options) {
  return compress(node, options);
}

/**
 * 
 * @param {array} arr 
 * @param {object} options 
 * @param {string} jPath 
 * @returns object
 */
function compress(arr, options, jPath) {
  let text;
  const compressedObj = {};
  for (let i = 0; i < arr.length; i++) {
    const tagObj = arr[i];
    const property = propName$1(tagObj);
    let newJpath = "";
    if (jPath === undefined) newJpath = property;else newJpath = jPath + "." + property;
    if (property === options.textNodeName) {
      if (text === undefined) text = tagObj[property];else text += "" + tagObj[property];
    } else if (property === undefined) {
      continue;
    } else if (tagObj[property]) {
      let val = compress(tagObj[property], options, newJpath);
      const isLeaf = isLeafTag(val, options);
      if (tagObj[":@"]) {
        assignAttributes(val, tagObj[":@"], newJpath, options);
      } else if (Object.keys(val).length === 1 && val[options.textNodeName] !== undefined && !options.alwaysCreateTextNode) {
        val = val[options.textNodeName];
      } else if (Object.keys(val).length === 0) {
        if (options.alwaysCreateTextNode) val[options.textNodeName] = "";else val = "";
      }
      if (compressedObj[property] !== undefined && compressedObj.hasOwnProperty(property)) {
        if (!Array.isArray(compressedObj[property])) {
          compressedObj[property] = [compressedObj[property]];
        }
        compressedObj[property].push(val);
      } else {
        //TODO: if a node is not an array, then check if it should be an array
        //also determine if it is a leaf node
        if (options.isArray(property, newJpath, isLeaf)) {
          compressedObj[property] = [val];
        } else {
          compressedObj[property] = val;
        }
      }
    }
  }
  // if(text && text.length > 0) compressedObj[options.textNodeName] = text;
  if (typeof text === "string") {
    if (text.length > 0) compressedObj[options.textNodeName] = text;
  } else if (text !== undefined) compressedObj[options.textNodeName] = text;
  return compressedObj;
}
function propName$1(obj) {
  const keys = Object.keys(obj);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    if (key !== ":@") return key;
  }
}
function assignAttributes(obj, attrMap, jpath, options) {
  if (attrMap) {
    const keys = Object.keys(attrMap);
    const len = keys.length; //don't make it inline
    for (let i = 0; i < len; i++) {
      const atrrName = keys[i];
      if (options.isArray(atrrName, jpath + "." + atrrName, true, true)) {
        obj[atrrName] = [attrMap[atrrName]];
      } else {
        obj[atrrName] = attrMap[atrrName];
      }
    }
  }
}
function isLeafTag(obj, options) {
  const {
    textNodeName
  } = options;
  const propCount = Object.keys(obj).length;
  if (propCount === 0) {
    return true;
  }
  if (propCount === 1 && (obj[textNodeName] || typeof obj[textNodeName] === "boolean" || obj[textNodeName] === 0)) {
    return true;
  }
  return false;
}
node2json.prettify = prettify$1;

const {
  buildOptions
} = OptionsBuilder;
const OrderedObjParser = OrderedObjParser_1;
const {
  prettify
} = node2json;
const validator$1 = validator$2;
let XMLParser$1 = class XMLParser {
  constructor(options) {
    this.externalEntities = {};
    this.options = buildOptions(options);
  }
  /**
   * Parse XML dats to JS object 
   * @param {string|Buffer} xmlData 
   * @param {boolean|Object} validationOption 
   */
  parse(xmlData, validationOption) {
    if (typeof xmlData === "string") ; else if (xmlData.toString) {
      xmlData = xmlData.toString();
    } else {
      throw new Error("XML data is accepted in String or Bytes[] form.");
    }
    if (validationOption) {
      if (validationOption === true) validationOption = {}; //validate with default options

      const result = validator$1.validate(xmlData, validationOption);
      if (result !== true) {
        throw Error(`${result.err.msg}:${result.err.line}:${result.err.col}`);
      }
    }
    const orderedObjParser = new OrderedObjParser(this.options);
    orderedObjParser.addExternalEntities(this.externalEntities);
    const orderedResult = orderedObjParser.parseXml(xmlData);
    if (this.options.preserveOrder || orderedResult === undefined) return orderedResult;else return prettify(orderedResult, this.options);
  }

  /**
   * Add Entity which is not by default supported by this library
   * @param {string} key 
   * @param {string} value 
   */
  addEntity(key, value) {
    if (value.indexOf("&") !== -1) {
      throw new Error("Entity value can't have '&'");
    } else if (key.indexOf("&") !== -1 || key.indexOf(";") !== -1) {
      throw new Error("An entity must be set without '&' and ';'. Eg. use '#xD' for '&#xD;'");
    } else if (value === "&") {
      throw new Error("An entity with value '&' is not permitted");
    } else {
      this.externalEntities[key] = value;
    }
  }
};
var XMLParser_1 = XMLParser$1;

const EOL = "\n";

/**
 * 
 * @param {array} jArray 
 * @param {any} options 
 * @returns 
 */
function toXml(jArray, options) {
  let indentation = "";
  if (options.format && options.indentBy.length > 0) {
    indentation = EOL;
  }
  return arrToStr(jArray, options, "", indentation);
}
function arrToStr(arr, options, jPath, indentation) {
  let xmlStr = "";
  let isPreviousElementTag = false;
  for (let i = 0; i < arr.length; i++) {
    const tagObj = arr[i];
    const tagName = propName(tagObj);
    if (tagName === undefined) continue;
    let newJPath = "";
    if (jPath.length === 0) newJPath = tagName;else newJPath = `${jPath}.${tagName}`;
    if (tagName === options.textNodeName) {
      let tagText = tagObj[tagName];
      if (!isStopNode(newJPath, options)) {
        tagText = options.tagValueProcessor(tagName, tagText);
        tagText = replaceEntitiesValue(tagText, options);
      }
      if (isPreviousElementTag) {
        xmlStr += indentation;
      }
      xmlStr += tagText;
      isPreviousElementTag = false;
      continue;
    } else if (tagName === options.cdataPropName) {
      if (isPreviousElementTag) {
        xmlStr += indentation;
      }
      xmlStr += `<![CDATA[${tagObj[tagName][0][options.textNodeName]}]]>`;
      isPreviousElementTag = false;
      continue;
    } else if (tagName === options.commentPropName) {
      xmlStr += indentation + `<!--${tagObj[tagName][0][options.textNodeName]}-->`;
      isPreviousElementTag = true;
      continue;
    } else if (tagName[0] === "?") {
      const attStr = attr_to_str(tagObj[":@"], options);
      const tempInd = tagName === "?xml" ? "" : indentation;
      let piTextNodeName = tagObj[tagName][0][options.textNodeName];
      piTextNodeName = piTextNodeName.length !== 0 ? " " + piTextNodeName : ""; //remove extra spacing
      xmlStr += tempInd + `<${tagName}${piTextNodeName}${attStr}?>`;
      isPreviousElementTag = true;
      continue;
    }
    let newIdentation = indentation;
    if (newIdentation !== "") {
      newIdentation += options.indentBy;
    }
    const attStr = attr_to_str(tagObj[":@"], options);
    const tagStart = indentation + `<${tagName}${attStr}`;
    const tagValue = arrToStr(tagObj[tagName], options, newJPath, newIdentation);
    if (options.unpairedTags.indexOf(tagName) !== -1) {
      if (options.suppressUnpairedNode) xmlStr += tagStart + ">";else xmlStr += tagStart + "/>";
    } else if ((!tagValue || tagValue.length === 0) && options.suppressEmptyNode) {
      xmlStr += tagStart + "/>";
    } else if (tagValue && tagValue.endsWith(">")) {
      xmlStr += tagStart + `>${tagValue}${indentation}</${tagName}>`;
    } else {
      xmlStr += tagStart + ">";
      if (tagValue && indentation !== "" && (tagValue.includes("/>") || tagValue.includes("</"))) {
        xmlStr += indentation + options.indentBy + tagValue + indentation;
      } else {
        xmlStr += tagValue;
      }
      xmlStr += `</${tagName}>`;
    }
    isPreviousElementTag = true;
  }
  return xmlStr;
}
function propName(obj) {
  const keys = Object.keys(obj);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    if (!obj.hasOwnProperty(key)) continue;
    if (key !== ":@") return key;
  }
}
function attr_to_str(attrMap, options) {
  let attrStr = "";
  if (attrMap && !options.ignoreAttributes) {
    for (let attr in attrMap) {
      if (!attrMap.hasOwnProperty(attr)) continue;
      let attrVal = options.attributeValueProcessor(attr, attrMap[attr]);
      attrVal = replaceEntitiesValue(attrVal, options);
      if (attrVal === true && options.suppressBooleanAttributes) {
        attrStr += ` ${attr.substr(options.attributeNamePrefix.length)}`;
      } else {
        attrStr += ` ${attr.substr(options.attributeNamePrefix.length)}="${attrVal}"`;
      }
    }
  }
  return attrStr;
}
function isStopNode(jPath, options) {
  jPath = jPath.substr(0, jPath.length - options.textNodeName.length - 1);
  let tagName = jPath.substr(jPath.lastIndexOf(".") + 1);
  for (let index in options.stopNodes) {
    if (options.stopNodes[index] === jPath || options.stopNodes[index] === "*." + tagName) return true;
  }
  return false;
}
function replaceEntitiesValue(textValue, options) {
  if (textValue && textValue.length > 0 && options.processEntities) {
    for (let i = 0; i < options.entities.length; i++) {
      const entity = options.entities[i];
      textValue = textValue.replace(entity.regex, entity.val);
    }
  }
  return textValue;
}
var orderedJs2Xml = toXml;

//parse Empty Node as self closing node
const buildFromOrderedJs = orderedJs2Xml;
const defaultOptions = {
  attributeNamePrefix: '@_',
  attributesGroupName: false,
  textNodeName: '#text',
  ignoreAttributes: true,
  cdataPropName: false,
  format: false,
  indentBy: '  ',
  suppressEmptyNode: false,
  suppressUnpairedNode: true,
  suppressBooleanAttributes: true,
  tagValueProcessor: function (key, a) {
    return a;
  },
  attributeValueProcessor: function (attrName, a) {
    return a;
  },
  preserveOrder: false,
  commentPropName: false,
  unpairedTags: [],
  entities: [{
    regex: new RegExp("&", "g"),
    val: "&amp;"
  },
  //it must be on top
  {
    regex: new RegExp(">", "g"),
    val: "&gt;"
  }, {
    regex: new RegExp("<", "g"),
    val: "&lt;"
  }, {
    regex: new RegExp("\'", "g"),
    val: "&apos;"
  }, {
    regex: new RegExp("\"", "g"),
    val: "&quot;"
  }],
  processEntities: true,
  stopNodes: [],
  // transformTagName: false,
  // transformAttributeName: false,
  oneListGroup: false
};
function Builder(options) {
  this.options = Object.assign({}, defaultOptions, options);
  if (this.options.ignoreAttributes || this.options.attributesGroupName) {
    this.isAttribute = function /*a*/
    () {
      return false;
    };
  } else {
    this.attrPrefixLen = this.options.attributeNamePrefix.length;
    this.isAttribute = isAttribute;
  }
  this.processTextOrObjNode = processTextOrObjNode;
  if (this.options.format) {
    this.indentate = indentate;
    this.tagEndChar = '>\n';
    this.newLine = '\n';
  } else {
    this.indentate = function () {
      return '';
    };
    this.tagEndChar = '>';
    this.newLine = '';
  }
}
Builder.prototype.build = function (jObj) {
  if (this.options.preserveOrder) {
    return buildFromOrderedJs(jObj, this.options);
  } else {
    if (Array.isArray(jObj) && this.options.arrayNodeName && this.options.arrayNodeName.length > 1) {
      jObj = {
        [this.options.arrayNodeName]: jObj
      };
    }
    return this.j2x(jObj, 0).val;
  }
};
Builder.prototype.j2x = function (jObj, level) {
  let attrStr = '';
  let val = '';
  for (let key in jObj) {
    if (!Object.prototype.hasOwnProperty.call(jObj, key)) continue;
    if (typeof jObj[key] === 'undefined') {
      // supress undefined node only if it is not an attribute
      if (this.isAttribute(key)) {
        val += '';
      }
    } else if (jObj[key] === null) {
      // null attribute should be ignored by the attribute list, but should not cause the tag closing
      if (this.isAttribute(key)) {
        val += '';
      } else if (key[0] === '?') {
        val += this.indentate(level) + '<' + key + '?' + this.tagEndChar;
      } else {
        val += this.indentate(level) + '<' + key + '/' + this.tagEndChar;
      }
      // val += this.indentate(level) + '<' + key + '/' + this.tagEndChar;
    } else if (jObj[key] instanceof Date) {
      val += this.buildTextValNode(jObj[key], key, '', level);
    } else if (typeof jObj[key] !== 'object') {
      //premitive type
      const attr = this.isAttribute(key);
      if (attr) {
        attrStr += this.buildAttrPairStr(attr, '' + jObj[key]);
      } else {
        //tag value
        if (key === this.options.textNodeName) {
          let newval = this.options.tagValueProcessor(key, '' + jObj[key]);
          val += this.replaceEntitiesValue(newval);
        } else {
          val += this.buildTextValNode(jObj[key], key, '', level);
        }
      }
    } else if (Array.isArray(jObj[key])) {
      //repeated nodes
      const arrLen = jObj[key].length;
      let listTagVal = "";
      let listTagAttr = "";
      for (let j = 0; j < arrLen; j++) {
        const item = jObj[key][j];
        if (typeof item === 'undefined') ; else if (item === null) {
          if (key[0] === "?") val += this.indentate(level) + '<' + key + '?' + this.tagEndChar;else val += this.indentate(level) + '<' + key + '/' + this.tagEndChar;
          // val += this.indentate(level) + '<' + key + '/' + this.tagEndChar;
        } else if (typeof item === 'object') {
          if (this.options.oneListGroup) {
            const result = this.j2x(item, level + 1);
            listTagVal += result.val;
            if (this.options.attributesGroupName && item.hasOwnProperty(this.options.attributesGroupName)) {
              listTagAttr += result.attrStr;
            }
          } else {
            listTagVal += this.processTextOrObjNode(item, key, level);
          }
        } else {
          if (this.options.oneListGroup) {
            let textValue = this.options.tagValueProcessor(key, item);
            textValue = this.replaceEntitiesValue(textValue);
            listTagVal += textValue;
          } else {
            listTagVal += this.buildTextValNode(item, key, '', level);
          }
        }
      }
      if (this.options.oneListGroup) {
        listTagVal = this.buildObjectNode(listTagVal, key, listTagAttr, level);
      }
      val += listTagVal;
    } else {
      //nested node
      if (this.options.attributesGroupName && key === this.options.attributesGroupName) {
        const Ks = Object.keys(jObj[key]);
        const L = Ks.length;
        for (let j = 0; j < L; j++) {
          attrStr += this.buildAttrPairStr(Ks[j], '' + jObj[key][Ks[j]]);
        }
      } else {
        val += this.processTextOrObjNode(jObj[key], key, level);
      }
    }
  }
  return {
    attrStr: attrStr,
    val: val
  };
};
Builder.prototype.buildAttrPairStr = function (attrName, val) {
  val = this.options.attributeValueProcessor(attrName, '' + val);
  val = this.replaceEntitiesValue(val);
  if (this.options.suppressBooleanAttributes && val === "true") {
    return ' ' + attrName;
  } else return ' ' + attrName + '="' + val + '"';
};
function processTextOrObjNode(object, key, level) {
  const result = this.j2x(object, level + 1);
  if (object[this.options.textNodeName] !== undefined && Object.keys(object).length === 1) {
    return this.buildTextValNode(object[this.options.textNodeName], key, result.attrStr, level);
  } else {
    return this.buildObjectNode(result.val, key, result.attrStr, level);
  }
}
Builder.prototype.buildObjectNode = function (val, key, attrStr, level) {
  if (val === "") {
    if (key[0] === "?") return this.indentate(level) + '<' + key + attrStr + '?' + this.tagEndChar;else {
      return this.indentate(level) + '<' + key + attrStr + this.closeTag(key) + this.tagEndChar;
    }
  } else {
    let tagEndExp = '</' + key + this.tagEndChar;
    let piClosingChar = "";
    if (key[0] === "?") {
      piClosingChar = "?";
      tagEndExp = "";
    }

    // attrStr is an empty string in case the attribute came as undefined or null
    if ((attrStr || attrStr === '') && val.indexOf('<') === -1) {
      return this.indentate(level) + '<' + key + attrStr + piClosingChar + '>' + val + tagEndExp;
    } else if (this.options.commentPropName !== false && key === this.options.commentPropName && piClosingChar.length === 0) {
      return this.indentate(level) + `<!--${val}-->` + this.newLine;
    } else {
      return this.indentate(level) + '<' + key + attrStr + piClosingChar + this.tagEndChar + val + this.indentate(level) + tagEndExp;
    }
  }
};
Builder.prototype.closeTag = function (key) {
  let closeTag = "";
  if (this.options.unpairedTags.indexOf(key) !== -1) {
    //unpaired
    if (!this.options.suppressUnpairedNode) closeTag = "/";
  } else if (this.options.suppressEmptyNode) {
    //empty
    closeTag = "/";
  } else {
    closeTag = `></${key}`;
  }
  return closeTag;
};
Builder.prototype.buildTextValNode = function (val, key, attrStr, level) {
  if (this.options.cdataPropName !== false && key === this.options.cdataPropName) {
    return this.indentate(level) + `<![CDATA[${val}]]>` + this.newLine;
  } else if (this.options.commentPropName !== false && key === this.options.commentPropName) {
    return this.indentate(level) + `<!--${val}-->` + this.newLine;
  } else if (key[0] === "?") {
    //PI tag
    return this.indentate(level) + '<' + key + attrStr + '?' + this.tagEndChar;
  } else {
    let textValue = this.options.tagValueProcessor(key, val);
    textValue = this.replaceEntitiesValue(textValue);
    if (textValue === '') {
      return this.indentate(level) + '<' + key + attrStr + this.closeTag(key) + this.tagEndChar;
    } else {
      return this.indentate(level) + '<' + key + attrStr + '>' + textValue + '</' + key + this.tagEndChar;
    }
  }
};
Builder.prototype.replaceEntitiesValue = function (textValue) {
  if (textValue && textValue.length > 0 && this.options.processEntities) {
    for (let i = 0; i < this.options.entities.length; i++) {
      const entity = this.options.entities[i];
      textValue = textValue.replace(entity.regex, entity.val);
    }
  }
  return textValue;
};
function indentate(level) {
  return this.options.indentBy.repeat(level);
}
function isAttribute(name /*, options*/) {
  if (name.startsWith(this.options.attributeNamePrefix) && name !== this.options.textNodeName) {
    return name.substr(this.attrPrefixLen);
  } else {
    return false;
  }
}
var json2xml = Builder;

const validator = validator$2;
const XMLParser = XMLParser_1;
const XMLBuilder = json2xml;
var fxp = {
  XMLParser: XMLParser,
  XMLValidator: validator,
  XMLBuilder: XMLBuilder
};

const fastXmlParser = /*@__PURE__*/getDefaultExportFromCjs(fxp);

let OB11UserSex = /* @__PURE__ */ function(OB11UserSex2) {
  OB11UserSex2["male"] = "male";
  OB11UserSex2["female"] = "female";
  OB11UserSex2["unknown"] = "unknown";
  return OB11UserSex2;
}({});
let OB11GroupMemberRole = /* @__PURE__ */ function(OB11GroupMemberRole2) {
  OB11GroupMemberRole2["owner"] = "owner";
  OB11GroupMemberRole2["admin"] = "admin";
  OB11GroupMemberRole2["member"] = "member";
  return OB11GroupMemberRole2;
}({});

let OB11MessageDataType = /* @__PURE__ */ function(OB11MessageDataType2) {
  OB11MessageDataType2["text"] = "text";
  OB11MessageDataType2["image"] = "image";
  OB11MessageDataType2["music"] = "music";
  OB11MessageDataType2["video"] = "video";
  OB11MessageDataType2["voice"] = "record";
  OB11MessageDataType2["file"] = "file";
  OB11MessageDataType2["at"] = "at";
  OB11MessageDataType2["reply"] = "reply";
  OB11MessageDataType2["json"] = "json";
  OB11MessageDataType2["face"] = "face";
  OB11MessageDataType2["mface"] = "mface";
  OB11MessageDataType2["markdown"] = "markdown";
  OB11MessageDataType2["node"] = "node";
  OB11MessageDataType2["forward"] = "forward";
  OB11MessageDataType2["xml"] = "xml";
  OB11MessageDataType2["poke"] = "poke";
  OB11MessageDataType2["dice"] = "dice";
  OB11MessageDataType2["RPS"] = "rps";
  OB11MessageDataType2["miniapp"] = "miniapp";
  OB11MessageDataType2["Location"] = "location";
  return OB11MessageDataType2;
}({});

function _defineProperty$1G(e, r, t) {
  return (r = _toPropertyKey$1G(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1G(t) {
  var i = _toPrimitive$1G(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1G(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
let EventType = /* @__PURE__ */ function(EventType2) {
  EventType2["META"] = "meta_event";
  EventType2["REQUEST"] = "request";
  EventType2["NOTICE"] = "notice";
  EventType2["MESSAGE"] = "message";
  EventType2["MESSAGE_SENT"] = "message_sent";
  return EventType2;
}({});
class OB11BaseEvent {
  constructor() {
    _defineProperty$1G(this, "time", Math.floor(Date.now() / 1e3));
    _defineProperty$1G(this, "self_id", parseInt(selfInfo.uin));
    _defineProperty$1G(this, "post_type", EventType.META);
  }
}

const pattern$1 = /\[CQ:(\w+)((,\w+=[^,\]]*)*)\]/;
function unescape$1(source) {
  return String(source).replace(/&#91;/g, "[").replace(/&#93;/g, "]").replace(/&#44;/g, ",").replace(/&amp;/g, "&");
}
function from(source) {
  const capture = pattern$1.exec(source);
  if (!capture) return null;
  const [, type, attrs] = capture;
  const data = {};
  attrs && attrs.slice(1).split(",").forEach((str) => {
    const index = str.indexOf("=");
    data[str.slice(0, index)] = unescape$1(str.slice(index + 1));
  });
  return {
    type,
    data,
    capture
  };
}
function h(type, data) {
  return {
    type,
    data
  };
}
function decodeCQCode(source) {
  const elements = [];
  let result;
  while (result = from(source)) {
    const {
      type,
      data,
      capture
    } = result;
    if (capture.index) {
      elements.push(h("text", {
        text: unescape$1(source.slice(0, capture.index))
      }));
    }
    elements.push(h(type, data));
    source = source.slice(capture.index + capture[0].length);
  }
  if (source) elements.push(h("text", {
    text: unescape$1(source)
  }));
  return elements;
}
function encodeCQCode(data) {
  const CQCodeEscapeText = (text) => {
    return text.replace(/&/g, "&amp;").replace(/\[/g, "&#91;").replace(/\]/g, "&#93;");
  };
  const CQCodeEscape = (text) => {
    return text.replace(/&/g, "&amp;").replace(/\[/g, "&#91;").replace(/\]/g, "&#93;").replace(/,/g, "&#44;");
  };
  if (data.type === "text") {
    return CQCodeEscapeText(data.data.text);
  }
  let result = "[CQ:" + data.type;
  for (const name in data.data) {
    const value = data.data[name];
    if (value === void 0) {
      continue;
    }
    try {
      const text = value.toString();
      result += `,${name}=${CQCodeEscape(text)}`;
    } catch (error) {
    }
  }
  result += "]";
  return result;
}

function _defineProperty$1F(e, r, t) {
  return (r = _toPropertyKey$1F(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1F(t) {
  var i = _toPrimitive$1F(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1F(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11BaseNoticeEvent extends OB11BaseEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$1F(this, "post_type", EventType.NOTICE);
  }
}

function _defineProperty$1E(e, r, t) {
  return (r = _toPropertyKey$1E(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1E(t) {
  var i = _toPrimitive$1E(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1E(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupNoticeEvent extends OB11BaseNoticeEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$1E(this, "group_id", 0);
    _defineProperty$1E(this, "user_id", 0);
  }
}

function _defineProperty$1D(e, r, t) {
  return (r = _toPropertyKey$1D(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1D(t) {
  var i = _toPrimitive$1D(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1D(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupIncreaseEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, operatorId, subType = "approve") {
    super();
    _defineProperty$1D(this, "notice_type", "group_increase");
    _defineProperty$1D(this, "operator_id", void 0);
    _defineProperty$1D(this, "sub_type", void 0);
    this.group_id = groupId;
    this.operator_id = operatorId;
    this.user_id = userId;
    this.sub_type = subType;
  }
}

function _defineProperty$1C(e, r, t) {
  return (r = _toPropertyKey$1C(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1C(t) {
  var i = _toPrimitive$1C(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1C(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupBanEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, operatorId, duration, sub_type) {
    super();
    _defineProperty$1C(this, "notice_type", "group_ban");
    _defineProperty$1C(this, "operator_id", void 0);
    _defineProperty$1C(this, "duration", void 0);
    _defineProperty$1C(this, "sub_type", void 0);
    this.group_id = groupId;
    this.operator_id = operatorId;
    this.user_id = userId;
    this.duration = duration;
    this.sub_type = sub_type;
  }
}

function _defineProperty$1B(e, r, t) {
  return (r = _toPropertyKey$1B(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1B(t) {
  var i = _toPrimitive$1B(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1B(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupUploadNoticeEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, file) {
    super();
    _defineProperty$1B(this, "notice_type", "group_upload");
    _defineProperty$1B(this, "file", void 0);
    this.group_id = groupId;
    this.user_id = userId;
    this.file = file;
  }
}

function calcQQLevel(level) {
  const {
    crownNum,
    sunNum,
    moonNum,
    starNum
  } = level;
  return crownNum * 64 + sunNum * 16 + moonNum * 4 + starNum;
}

function _defineProperty$1A(e, r, t) {
  return (r = _toPropertyKey$1A(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1A(t) {
  var i = _toPrimitive$1A(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1A(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupTitleEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, title) {
    super();
    _defineProperty$1A(this, "notice_type", "notify");
    _defineProperty$1A(this, "sub_type", "title");
    _defineProperty$1A(this, "title", void 0);
    this.group_id = groupId;
    this.user_id = userId;
    this.title = title;
  }
}

function _defineProperty$1z(e, r, t) {
  return (r = _toPropertyKey$1z(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1z(t) {
  var i = _toPrimitive$1z(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1z(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupCardEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, cardNew, cardOld) {
    super();
    _defineProperty$1z(this, "notice_type", "group_card");
    _defineProperty$1z(this, "card_new", void 0);
    _defineProperty$1z(this, "card_old", void 0);
    this.group_id = groupId;
    this.user_id = userId;
    this.card_new = cardNew;
    this.card_old = cardOld;
  }
}

function _defineProperty$1y(e, r, t) {
  return (r = _toPropertyKey$1y(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1y(t) {
  var i = _toPrimitive$1y(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1y(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupDecreaseEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, operatorId, subType = "leave") {
    super();
    _defineProperty$1y(this, "notice_type", "group_decrease");
    _defineProperty$1y(this, "sub_type", "leave");
    _defineProperty$1y(this, "operator_id", void 0);
    this.group_id = groupId;
    this.operator_id = operatorId;
    this.user_id = userId;
    this.sub_type = subType;
  }
}

function _defineProperty$1x(e, r, t) {
  return (r = _toPropertyKey$1x(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1x(t) {
  var i = _toPrimitive$1x(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1x(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const __filename$5 = fileURLToPath(import.meta.url);
const __dirname$5 = dirname(__filename$5);
const configDir = path__default.resolve(__dirname$5, "config");
fs__default.mkdirSync(configDir, {
  recursive: true
});
class ConfigBase {
  // 本次读取的文件路径
  constructor() {
    _defineProperty$1x(this, "name", "default_config");
    _defineProperty$1x(this, "pathName", null);
  }
  getKeys() {
    return null;
  }
  getConfigDir() {
    const configDir2 = path__default.resolve(__dirname$5, "config");
    fs__default.mkdirSync(configDir2, {
      recursive: true
    });
    return configDir2;
  }
  getConfigPath(pathName) {
    const suffix = pathName ? `_${pathName}` : "";
    const filename = `${this.name}${suffix}.json`;
    return path__default.join(this.getConfigDir(), filename);
  }
  read() {
    if (this.read_from_file(selfInfo.uin, false)) return this;
    return this.read_from_file("", true);
  }
  read_from_file(pathName, createIfNotExist) {
    const configPath = this.getConfigPath(pathName);
    if (!fs__default.existsSync(configPath)) {
      if (!createIfNotExist) return null;
      this.pathName = pathName;
      try {
        fs__default.writeFileSync(configPath, JSON.stringify(this, this.getKeys(), 2));
        log(`配置文件${configPath}已创建
如果修改此文件后需要重启 NapCat 生效`);
      } catch (e) {
        logError(`创建配置文件 ${configPath} 时发生错误:`, e.message);
      }
      return this;
    }
    try {
      const data = JSON.parse(fs__default.readFileSync(configPath, "utf-8"));
      logDebug(`配置文件${configPath}已加载`, data);
      Object.assign(this, data);
      this.save(this);
      return this;
    } catch (e) {
      if (e instanceof SyntaxError) {
        logError(`配置文件 ${configPath} 格式错误，请检查配置文件:`, e.message);
      } else {
        logError(`读取配置文件 ${configPath} 时发生错误:`, e.message);
      }
      return this;
    }
  }
  save(config, overwrite = false) {
    Object.assign(this, config);
    if (overwrite) {
      this.pathName = `${selfInfo.uin}`;
    }
    const configPath = this.getConfigPath(this.pathName);
    try {
      fs__default.writeFileSync(configPath, JSON.stringify(this, this.getKeys(), 2));
    } catch (e) {
      logError(`保存配置文件 ${configPath} 时发生错误:`, e.message);
    }
  }
}

function _defineProperty$1w(e, r, t) {
  return (r = _toPropertyKey$1w(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1w(t) {
  var i = _toPrimitive$1w(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1w(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
let Config$1 = class Config extends ConfigBase {
  constructor(...args) {
    super(...args);
    _defineProperty$1w(this, "name", "onebot11");
    _defineProperty$1w(this, "http", {
      enable: false,
      host: "",
      port: 3e3,
      secret: "",
      enableHeart: false,
      enablePost: false,
      postUrls: []
    });
    _defineProperty$1w(this, "ws", {
      enable: false,
      host: "",
      port: 3001
    });
    _defineProperty$1w(this, "reverseWs", {
      enable: false,
      urls: []
    });
    _defineProperty$1w(this, "debug", false);
    _defineProperty$1w(this, "heartInterval", 3e4);
    _defineProperty$1w(this, "messagePostFormat", "array");
    _defineProperty$1w(this, "enableLocalFile2Url", true);
    _defineProperty$1w(this, "musicSignUrl", "");
    _defineProperty$1w(this, "reportSelfMessage", false);
    _defineProperty$1w(this, "token", "");
    _defineProperty$1w(this, "GroupLocalTime", {
      Record: false,
      RecordList: []
    });
  }
  getKeys() {
    return null;
  }
};
const ob11Config = new Config$1();

function _defineProperty$1v(e, r, t) {
  return (r = _toPropertyKey$1v(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1v(t) {
  var i = _toPrimitive$1v(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1v(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupMsgEmojiLikeEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, messageId, likes) {
    super();
    _defineProperty$1v(this, "notice_type", "group_msg_emoji_like");
    _defineProperty$1v(this, "message_id", void 0);
    _defineProperty$1v(this, "likes", void 0);
    this.group_id = groupId;
    this.user_id = userId;
    this.message_id = messageId;
    this.likes = likes;
  }
}

function _defineProperty$1u(e, r, t) {
  return (r = _toPropertyKey$1u(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1u(t) {
  var i = _toPrimitive$1u(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1u(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11PokeEvent extends OB11BaseNoticeEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$1u(this, "notice_type", "notify");
    _defineProperty$1u(this, "sub_type", "poke");
    _defineProperty$1u(this, "target_id", 0);
    _defineProperty$1u(this, "user_id", 0);
  }
}
class OB11FriendPokeEvent extends OB11PokeEvent {
  //raw_message nb等框架标准为string
  constructor(user_id, target_id, raw_message) {
    super();
    _defineProperty$1u(this, "raw_info", void 0);
    this.target_id = target_id;
    this.user_id = user_id;
    this.raw_info = raw_message;
  }
}
class OB11GroupPokeEvent extends OB11PokeEvent {
  //raw_message nb等框架标准为string
  constructor(group_id, user_id = 0, target_id = 0, raw_message) {
    super();
    _defineProperty$1u(this, "group_id", void 0);
    _defineProperty$1u(this, "raw_info", void 0);
    this.group_id = group_id;
    this.target_id = target_id;
    this.user_id = user_id;
    this.raw_info = raw_message;
  }
}

function _defineProperty$1t(e, r, t) {
  return (r = _toPropertyKey$1t(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1t(t) {
  var i = _toPrimitive$1t(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1t(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11FriendAddNoticeEvent extends OB11BaseNoticeEvent {
  constructor(user_Id) {
    super();
    _defineProperty$1t(this, "notice_type", "friend_add");
    _defineProperty$1t(this, "user_id", void 0);
    this.user_id = user_Id;
  }
}

function _defineProperty$1s(e, r, t) {
  return (r = _toPropertyKey$1s(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1s(t) {
  var i = _toPrimitive$1s(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1s(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupEssenceEvent extends OB11GroupNoticeEvent {
  constructor(groupId, message_id, sender_id) {
    super();
    _defineProperty$1s(this, "notice_type", "essence");
    _defineProperty$1s(this, "message_id", void 0);
    _defineProperty$1s(this, "sender_id", void 0);
    _defineProperty$1s(this, "sub_type", "add");
    this.group_id = groupId;
    this.message_id = message_id;
    this.sender_id = sender_id;
  }
}

class OB11Constructor {
  static async message(msg) {
    const {
      messagePostFormat
    } = ob11Config;
    msg.chatType == ChatType.group ? "group" : "private";
    const resMsg = {
      self_id: parseInt(selfInfo.uin),
      user_id: parseInt(msg.senderUin),
      time: parseInt(msg.msgTime) || Date.now(),
      message_id: msg.id,
      message_seq: msg.id,
      real_id: msg.id,
      message_type: msg.chatType == ChatType.group ? "group" : "private",
      sender: {
        user_id: parseInt(msg.senderUin || "0"),
        nickname: msg.sendNickName,
        card: msg.sendMemberName || ""
      },
      raw_message: "",
      font: 14,
      sub_type: "friend",
      message: messagePostFormat === "string" ? "" : [],
      message_format: messagePostFormat === "string" ? "string" : "array",
      post_type: selfInfo.uin == msg.senderUin ? EventType.MESSAGE_SENT : EventType.MESSAGE
    };
    if (msg.chatType == ChatType.group) {
      resMsg.sub_type = "normal";
      resMsg.group_id = parseInt(msg.peerUin);
      let member = await getGroupMember(msg.peerUin, msg.senderUin);
      if (!member) {
        const memberList = await NTQQGroupApi.getGroupMembers(msg.peerUin);
        member = memberList.get(msg.senderUin);
      }
      if (member) {
        resMsg.sender.role = OB11Constructor.groupMemberRole(member.role);
        resMsg.sender.nickname = member.nick;
      }
    } else if (msg.chatType == ChatType.friend) {
      resMsg.sub_type = "friend";
      resMsg.sender.nickname = (await NTQQUserApi.getUserDetailInfo(msg.senderUid)).nick;
    } else if (msg.chatType == ChatType2.KCHATTYPETEMPC2CFROMGROUP) {
      resMsg.sub_type = "group";
      let ret = await NTQQMsgApi.getTempChatInfo(ChatType2.KCHATTYPETEMPC2CFROMGROUP, msg.senderUid);
      if (ret.result === 0) {
        resMsg.group_id = parseInt(ret.tmpChatInfo.groupCode);
        resMsg.sender.nickname = ret.tmpChatInfo.fromNick;
      } else {
        resMsg.group_id = 284840486;
        resMsg.sender.nickname = "临时会话";
      }
    }
    for (const element of msg.elements) {
      let message_data = {
        data: {},
        type: "unknown"
      };
      if (element.textElement && element.textElement?.atType !== AtType.notAt) {
        let qq;
        let name;
        if (element.textElement.atType == AtType.atAll) {
          qq = "all";
        } else {
          const {
            atNtUid,
            content
          } = element.textElement;
          let atQQ = element.textElement.atUid;
          if (!atQQ || atQQ === "0") {
            const atMember = await getGroupMember(msg.peerUin, atNtUid);
            if (atMember) {
              atQQ = atMember.uin;
            }
          }
          if (atQQ) {
            qq = atQQ;
            name = content.replace("@", "");
          }
        }
        message_data = {
          type: OB11MessageDataType.at,
          data: {
            qq,
            name
          }
        };
      } else if (element.textElement) {
        message_data["type"] = OB11MessageDataType.text;
        let text = element.textElement.content;
        if (!text.trim()) {
          continue;
        }
        if (text.indexOf("\n") === -1 && text.indexOf("\r\n") === -1) {
          text = text.replace(/\r/g, "\n");
        }
        message_data["data"]["text"] = text;
      } else if (element.replyElement) {
        message_data["type"] = OB11MessageDataType.reply;
        try {
          const records = msg.records.find((msgRecord) => msgRecord.msgId === element.replyElement.sourceMsgIdInRecords);
          const peer = {
            chatType: msg.chatType,
            peerUid: msg.peerUid,
            guildId: ""
          };
          let replyMsg;
          if (!records) throw new Error("找不到回复消息");
          replyMsg = (await NTQQMsgApi.getMsgsBySeqAndCount({
            peerUid: msg.peerUid,
            guildId: "",
            chatType: msg.chatType
          }, element.replyElement.replayMsgSeq, 1, true, true)).msgList[0];
          if (!replyMsg || records.msgRandom !== replyMsg.msgRandom) {
            replyMsg = (await NTQQMsgApi.getSingleMsg(peer, element.replyElement.replayMsgSeq)).msgList[0];
          }
          if (msg.peerUin == "284840486") {
          }
          if ((!replyMsg || records.msgRandom !== replyMsg.msgRandom) && msg.peerUin !== "284840486") {
            throw new Error("回复消息消息验证失败");
          }
          message_data["data"]["id"] = MessageUnique.createMsg({
            peerUid: msg.peerUid,
            guildId: "",
            chatType: msg.chatType
          }, replyMsg.msgId)?.toString();
        } catch (e) {
          message_data["type"] = "unknown";
          message_data["data"] = void 0;
          logError("获取不到引用的消息", e.stack, element.replyElement.replayMsgSeq);
        }
      } else if (element.picElement) {
        message_data["type"] = OB11MessageDataType.image;
        message_data["data"]["file"] = element.picElement.fileName;
        message_data["data"]["subType"] = element.picElement.picSubType;
        message_data["data"]["file_id"] = UUIDConverter.encode(msg.peerUin, msg.msgId);
        try {
          message_data["data"]["url"] = await NTQQFileApi.getImageUrl(element.picElement);
        } catch (e) {
          logError("获取图片url失败", e.stack);
        }
        message_data["data"]["file_size"] = element.picElement.fileSize;
      } else if (element.fileElement) {
        const FileElement = element.fileElement;
        message_data["type"] = OB11MessageDataType.file;
        message_data["data"]["file"] = FileElement.fileName;
        message_data["data"]["path"] = FileElement.filePath;
        message_data["data"]["url"] = FileElement.filePath;
        message_data["data"]["file_id"] = UUIDConverter.encode(msg.peerUin, msg.msgId);
        message_data["data"]["file_size"] = FileElement.fileSize;
        await NTQQFileApi.addFileCache({
          peerUid: msg.peerUid,
          chatType: msg.chatType,
          guildId: ""
        }, msg.msgId, msg.msgSeq, msg.senderUid, element.elementId, element.elementType.toString(), FileElement.fileSize, FileElement.fileName);
      } else if (element.videoElement) {
        const videoElement = element.videoElement;
        let videoUrl;
        let peer = {
          chatType: msg.chatType,
          peerUid: msg.peerUid,
          guildId: "0"
        };
        if (msg.peerUin == "284840486") {
          peer = msg.parentMsgPeer;
        }
        try {
          videoUrl = await NTQQFileApi.getVideoUrl(peer, msg.msgId, element.elementId);
        } catch (error) {
          videoUrl = void 0;
        }
        let videoDownUrl = void 0;
        if (videoUrl) {
          const videoDownUrlTemp = videoUrl.find((url) => {
            if (url.url) {
              return true;
            }
            return false;
          });
          if (videoDownUrlTemp) {
            videoDownUrl = videoDownUrlTemp.url;
          }
        }
        if (!videoDownUrl) {
          videoDownUrl = videoElement.filePath;
        }
        message_data["type"] = OB11MessageDataType.video;
        message_data["data"]["file"] = videoElement.fileName;
        message_data["data"]["path"] = videoDownUrl;
        message_data["data"]["url"] = videoDownUrl;
        message_data["data"]["file_id"] = UUIDConverter.encode(msg.peerUin, msg.msgId);
        message_data["data"]["file_size"] = videoElement.fileSize;
        await NTQQFileApi.addFileCache({
          peerUid: msg.peerUid,
          chatType: msg.chatType,
          guildId: ""
        }, msg.msgId, msg.msgSeq, msg.senderUid, element.elementId, element.elementType.toString(), videoElement.fileSize || "0", videoElement.fileName);
      } else if (element.pttElement) {
        message_data["type"] = OB11MessageDataType.voice;
        message_data["data"]["file"] = element.pttElement.fileName;
        message_data["data"]["path"] = element.pttElement.filePath;
        message_data["data"]["file_id"] = UUIDConverter.encode(msg.peerUin, msg.msgId);
        message_data["data"]["file_size"] = element.pttElement.fileSize;
        await NTQQFileApi.addFileCache({
          peerUid: msg.peerUid,
          chatType: msg.chatType,
          guildId: ""
        }, msg.msgId, msg.msgSeq, msg.senderUid, element.elementId, element.elementType.toString(), element.pttElement.fileSize || "0", element.pttElement.fileUuid || "");
      } else if (element.arkElement) {
        message_data["type"] = OB11MessageDataType.json;
        message_data["data"]["data"] = element.arkElement.bytesData;
      } else if (element.faceElement) {
        const faceId = element.faceElement.faceIndex;
        if (faceId === FaceIndex.dice) {
          message_data["type"] = OB11MessageDataType.dice;
          message_data["data"]["result"] = element.faceElement.resultId;
        } else if (faceId === FaceIndex.RPS) {
          message_data["type"] = OB11MessageDataType.RPS;
          message_data["data"]["result"] = element.faceElement.resultId;
        } else {
          message_data["type"] = OB11MessageDataType.face;
          message_data["data"]["id"] = element.faceElement.faceIndex.toString();
        }
      } else if (element.marketFaceElement) {
        message_data["type"] = OB11MessageDataType.mface;
        message_data["data"]["summary"] = element.marketFaceElement.faceName;
        const md5 = element.marketFaceElement.emojiId;
        const dir = md5.substring(0, 2);
        const url = `https://gxh.vip.qq.com/club/item/parcel/item/${dir}/${md5}/raw300.gif`;
        message_data["data"]["url"] = url;
        message_data["data"]["emoji_id"] = element.marketFaceElement.emojiId;
        message_data["data"]["emoji_package_id"] = String(element.marketFaceElement.emojiPackageId);
        message_data["data"]["key"] = element.marketFaceElement.key;
        mFaceCache.set(md5, element.marketFaceElement.faceName);
      } else if (element.markdownElement) {
        message_data["type"] = OB11MessageDataType.markdown;
        message_data["data"]["data"] = element.markdownElement.content;
      } else if (element.multiForwardMsgElement) {
        message_data["type"] = OB11MessageDataType.forward;
        message_data["data"]["id"] = msg.msgId;
        const ParentMsgPeer = msg.parentMsgPeer ?? {
          chatType: msg.chatType,
          guildId: "",
          peerUid: msg.peerUid
        };
        msg.parentMsgIdList = msg.parentMsgIdList ?? [];
        msg.parentMsgIdList.push(msg.msgId);
        const MultiMsgs = (await NTQQMsgApi.getMultiMsg(ParentMsgPeer, msg.parentMsgIdList[0], msg.msgId))?.msgList;
        if (!MultiMsgs) continue;
        message_data["data"]["content"] = [];
        for (const MultiMsg of MultiMsgs) {
          MultiMsg.parentMsgPeer = ParentMsgPeer;
          MultiMsg.parentMsgIdList = msg.parentMsgIdList;
          MultiMsg.id = MessageUnique.createMsg(ParentMsgPeer, MultiMsg.msgId);
          const msgList = await OB11Constructor.message(MultiMsg);
          message_data["data"]["content"].push(msgList);
        }
      }
      if (message_data.type !== "unknown" && message_data.data) {
        const cqCode = encodeCQCode(message_data);
        if (messagePostFormat === "string") {
          resMsg.message += cqCode;
        } else resMsg.message.push(message_data);
        resMsg.raw_message += cqCode;
      }
    }
    resMsg.raw_message = resMsg.raw_message.trim();
    return resMsg;
  }
  static async PrivateEvent(msg) {
    if (msg.chatType !== ChatType.friend) {
      return;
    }
    for (const element of msg.elements) {
      if (element.grayTipElement) {
        if (element.grayTipElement.subElementType == GrayTipElementSubType.MEMBER_NEW_TITLE) {
          const json = JSON.parse(element.grayTipElement.jsonGrayTipElement.jsonStr);
          if (element.grayTipElement.jsonGrayTipElement.busiId == 1061) {
            let pokedetail = json.items;
            pokedetail = pokedetail.filter((item) => item.uid);
            if (pokedetail.length == 2) {
              return new OB11FriendPokeEvent(parseInt(await NTQQUserApi.getUinByUid(pokedetail[0].uid)), parseInt(await NTQQUserApi.getUinByUid(pokedetail[1].uid)), pokedetail);
            }
          }
        }
        if (element.grayTipElement.subElementType == GrayTipElementSubType.INVITE_NEW_MEMBER) {
          if (element.grayTipElement.xmlElement.templId === "10229" && msg.peerUin !== "") {
            return new OB11FriendAddNoticeEvent(parseInt(msg.peerUin));
          }
        }
      }
    }
  }
  static async GroupEvent(msg) {
    if (msg.chatType !== ChatType.group) {
      return;
    }
    if (msg.senderUin && msg.senderUin !== "0") {
      const member = await getGroupMember(msg.peerUid, msg.senderUin);
      if (member && member.cardName !== msg.sendMemberName) {
        const newCardName = msg.sendMemberName || "";
        const event = new OB11GroupCardEvent(parseInt(msg.peerUid), parseInt(msg.senderUin), newCardName, member.cardName);
        member.cardName = newCardName;
        return event;
      }
    }
    for (const element of msg.elements) {
      const grayTipElement = element.grayTipElement;
      const groupElement = grayTipElement?.groupElement;
      if (groupElement) {
        if (groupElement.type == TipGroupElementType.memberIncrease) {
          logDebug("收到群成员增加消息", groupElement);
          await sleep(1e3);
          const member = await getGroupMember(msg.peerUid, groupElement.memberUid);
          const memberUin = member?.uin;
          const adminMember = await getGroupMember(msg.peerUid, groupElement.adminUid);
          if (memberUin) {
            const operatorUin = adminMember?.uin || memberUin;
            const event = new OB11GroupIncreaseEvent(parseInt(msg.peerUid), parseInt(memberUin), parseInt(operatorUin));
            return event;
          }
        } else if (groupElement.type === TipGroupElementType.ban) {
          logDebug("收到群群员禁言提示", groupElement);
          const memberUid = groupElement.shutUp.member.uid;
          const adminUid = groupElement.shutUp.admin.uid;
          let memberUin = "";
          let duration = parseInt(groupElement.shutUp.duration);
          const sub_type = duration > 0 ? "ban" : "lift_ban";
          if (memberUid) {
            memberUin = (await getGroupMember(msg.peerUid, memberUid))?.uin || "";
          } else {
            memberUin = "0";
            if (duration > 0) {
              duration = -1;
            }
          }
          const adminUin = (await getGroupMember(msg.peerUid, adminUid))?.uin;
          if (memberUin && adminUin) {
            const event = new OB11GroupBanEvent(parseInt(msg.peerUid), parseInt(memberUin), parseInt(adminUin), duration, sub_type);
            return event;
          }
        } else if (groupElement.type == TipGroupElementType.kicked) {
          logDebug(`收到我被踢出或退群提示, 群${msg.peerUid}`, groupElement);
          deleteGroup(msg.peerUid);
          NTQQGroupApi.quitGroup(msg.peerUid).then();
          try {
            const adminUin = (await getGroupMember(msg.peerUid, groupElement.adminUid))?.uin || await NTQQUserApi.getUidByUin(groupElement.adminUid);
            if (adminUin) {
              return new OB11GroupDecreaseEvent(parseInt(msg.peerUid), parseInt(selfInfo.uin), parseInt(adminUin), "kick_me");
            }
          } catch (e) {
            return new OB11GroupDecreaseEvent(parseInt(msg.peerUid), parseInt(selfInfo.uin), 0, "leave");
          }
        }
      } else if (element.fileElement) {
        return new OB11GroupUploadNoticeEvent(parseInt(msg.peerUid), parseInt(msg.senderUin || ""), {
          id: element.fileElement.fileUuid,
          name: element.fileElement.fileName,
          size: parseInt(element.fileElement.fileSize),
          busid: element.fileElement.fileBizId || 0
        });
      }
      if (grayTipElement) {
        if (grayTipElement.xmlElement?.templId === "10382") {
          const emojiLikeData = new fastXmlParser.XMLParser({
            ignoreAttributes: false,
            attributeNamePrefix: ""
          }).parse(grayTipElement.xmlElement.content);
          logDebug("收到表情回应我的消息", emojiLikeData);
          try {
            const senderUin = emojiLikeData.gtip.qq.jp;
            const msgSeq = emojiLikeData.gtip.url.msgseq;
            const emojiId = emojiLikeData.gtip.face.id;
            const replyMsgList = (await NTQQMsgApi.getMsgsBySeqAndCount({
              chatType: ChatType.group,
              guildId: "",
              peerUid: msg.peerUid
            }, msgSeq, 1, true, true)).msgList;
            if (replyMsgList.length < 1) {
              return;
            }
            const replyMsg = replyMsgList[0];
            return new OB11GroupMsgEmojiLikeEvent(parseInt(msg.peerUid), parseInt(senderUin), MessageUnique.getShortIdByMsgId(replyMsg?.msgId), [{
              emoji_id: emojiId,
              count: 1
            }]);
          } catch (e) {
            logError("解析表情回应消息失败", e.stack);
          }
        }
        if (grayTipElement.subElementType == GrayTipElementSubType.INVITE_NEW_MEMBER) {
          logDebug("收到新人被邀请进群消息", grayTipElement);
          const xmlElement = grayTipElement.xmlElement;
          if (xmlElement?.content) {
            const regex = /jp="(\d+)"/g;
            const matches = [];
            let match = null;
            while ((match = regex.exec(xmlElement.content)) !== null) {
              matches.push(match[1]);
            }
            if (matches.length === 2) {
              const [inviter, invitee] = matches;
              return new OB11GroupIncreaseEvent(parseInt(msg.peerUid), parseInt(invitee), parseInt(inviter), "invite");
            }
          }
        } else if (grayTipElement.subElementType == GrayTipElementSubType.MEMBER_NEW_TITLE) {
          const json = JSON.parse(grayTipElement.jsonGrayTipElement.jsonStr);
          if (grayTipElement.jsonGrayTipElement.busiId == 1061) {
            const pokedetail = json.items;
            const poke_uid = pokedetail.filter((item) => item.uid);
            if (poke_uid.length == 2) {
              return new OB11GroupPokeEvent(parseInt(msg.peerUid), parseInt(await NTQQUserApi.getUinByUid(poke_uid[0].uid)), parseInt(await NTQQUserApi.getUinByUid(poke_uid[1].uid)), pokedetail);
            }
          }
          if (grayTipElement.jsonGrayTipElement.busiId == 2401) {
            const searchParams = new URL(json.items[0].jp).searchParams;
            const msgSeq = searchParams.get("msgSeq");
            const Group = searchParams.get("groupCode");
            searchParams.get("businessid");
            const Peer = {
              guildId: "",
              chatType: ChatType.group,
              peerUid: Group
            };
            const msgData = await NTQQMsgApi.getMsgsBySeqAndCount(Peer, msgSeq.toString(), 1, true, true);
            return new OB11GroupEssenceEvent(parseInt(msg.peerUid), MessageUnique.getShortIdByMsgId(msgData.msgList[0].msgId), parseInt(msgData.msgList[0].senderUin));
          }
          if (grayTipElement.jsonGrayTipElement.busiId == 2407) {
            const memberUin = json.items[1].param[0];
            const title = json.items[3].txt;
            logDebug("收到群成员新头衔消息", json);
            return new OB11GroupTitleEvent(parseInt(msg.peerUid), parseInt(memberUin), title);
          }
        }
      }
    }
  }
  static friend(friend) {
    return {
      user_id: parseInt(friend.uin),
      nickname: friend.nick,
      remark: friend.remark,
      sex: OB11Constructor.sex(friend.sex),
      level: friend.qqLevel && calcQQLevel(friend.qqLevel) || 0
    };
  }
  static selfInfo(selfInfo2) {
    return {
      user_id: parseInt(selfInfo2.uin),
      nickname: selfInfo2.nick
    };
  }
  static friendsV2(friends) {
    const data = [];
    friends.forEach((friend) => {
      const sexValue = this.sex(friend.baseInfo.sex);
      data.push({
        ...friend.baseInfo,
        ...friend.coreInfo,
        user_id: parseInt(friend.coreInfo.uin),
        nickname: friend.coreInfo.nick,
        remark: friend.coreInfo.nick,
        sex: sexValue,
        level: 0,
        categroyName: friend.categroyName,
        categoryId: friend.categoryId
      });
    });
    return data;
  }
  static friends(friends) {
    const data = [];
    friends.forEach((friend) => {
      const sexValue = this.sex(friend.sex);
      data.push({
        user_id: parseInt(friend.uin),
        nickname: friend.nick,
        remark: friend.remark,
        sex: sexValue,
        level: 0
      });
    });
    return data;
  }
  static groupMemberRole(role) {
    return {
      4: OB11GroupMemberRole.owner,
      3: OB11GroupMemberRole.admin,
      2: OB11GroupMemberRole.member
    }[role];
  }
  static sex(sex) {
    const sexMap = {
      [Sex.male]: OB11UserSex.male,
      [Sex.female]: OB11UserSex.female,
      [Sex.unknown]: OB11UserSex.unknown
    };
    return sexMap[sex] || OB11UserSex.unknown;
  }
  static groupMember(group_id, member) {
    return {
      group_id: parseInt(group_id),
      user_id: parseInt(member.uin),
      nickname: member.nick,
      card: member.cardName,
      sex: OB11Constructor.sex(member.sex),
      age: 0,
      area: "",
      level: "0",
      qq_level: member.qqLevel && calcQQLevel(member.qqLevel) || 0,
      join_time: 0,
      // 暂时没法获取
      last_sent_time: 0,
      // 暂时没法获取
      title_expire_time: 0,
      unfriendly: false,
      card_changeable: true,
      is_robot: member.isRobot,
      shut_up_timestamp: member.shutUpTime,
      role: OB11Constructor.groupMemberRole(member.role),
      title: member.memberSpecialTitle || ""
    };
  }
  static stranger(user) {
    return {
      ...user,
      user_id: parseInt(user.uin),
      nickname: user.nick,
      sex: OB11Constructor.sex(user.sex),
      age: 0,
      qid: user.qid,
      login_days: 0,
      level: user.qqLevel && calcQQLevel(user.qqLevel) || 0
    };
  }
  static groupMembers(group) {
    return Array.from(groupMembers.get(group.groupCode)?.values() || []).map((m) => OB11Constructor.groupMember(group.groupCode, m));
  }
  static group(group) {
    return {
      group_id: parseInt(group.groupCode),
      group_name: group.groupName,
      member_count: group.memberCount,
      max_member_count: group.maxMember
    };
  }
  static groups(groups) {
    return groups.map(OB11Constructor.group);
  }
}

function wsReply(wsClient, data) {
  try {
    const packet = Object.assign({}, data);
    if (isNull(packet["echo"])) {
      delete packet["echo"];
    }
    wsClient.send(JSON.stringify(packet));
    logDebug("ws 消息上报", wsClient.url || "", data);
  } catch (e) {
    logError("websocket 回复失败", e.stack, data);
  }
}

class OB11Response {
  static res(data, status, retcode, message = "") {
    return {
      status,
      retcode,
      data,
      message,
      wording: message,
      echo: null
    };
  }
  static ok(data, echo = null) {
    const res = OB11Response.res(data, "ok", 0);
    if (!isNull(echo)) {
      res.echo = echo;
    }
    return res;
  }
  static error(err, retcode, echo = null) {
    const res = OB11Response.res(null, "failed", retcode, err);
    if (!isNull(echo)) {
      res.echo = echo;
    }
    return res;
  }
}

var ajv = {exports: {}};

var core$2 = {};

var validate = {};

var boolSchema = {};

var errors = {};

var codegen = {};

var code$1 = {};

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.regexpCode = exports.getEsmExportName = exports.getProperty = exports.safeStringify = exports.stringify = exports.strConcat = exports.addCodeArg = exports.str = exports._ = exports.nil = exports._Code = exports.Name = exports.IDENTIFIER = exports._CodeOrName = void 0;
	// eslint-disable-next-line @typescript-eslint/no-extraneous-class
	class _CodeOrName {}
	exports._CodeOrName = _CodeOrName;
	exports.IDENTIFIER = /^[a-z$_][a-z$_0-9]*$/i;
	class Name extends _CodeOrName {
	  constructor(s) {
	    super();
	    if (!exports.IDENTIFIER.test(s)) throw new Error("CodeGen: name must be a valid identifier");
	    this.str = s;
	  }
	  toString() {
	    return this.str;
	  }
	  emptyStr() {
	    return false;
	  }
	  get names() {
	    return {
	      [this.str]: 1
	    };
	  }
	}
	exports.Name = Name;
	class _Code extends _CodeOrName {
	  constructor(code) {
	    super();
	    this._items = typeof code === "string" ? [code] : code;
	  }
	  toString() {
	    return this.str;
	  }
	  emptyStr() {
	    if (this._items.length > 1) return false;
	    const item = this._items[0];
	    return item === "" || item === '""';
	  }
	  get str() {
	    var _a;
	    return (_a = this._str) !== null && _a !== void 0 ? _a : this._str = this._items.reduce((s, c) => `${s}${c}`, "");
	  }
	  get names() {
	    var _a;
	    return (_a = this._names) !== null && _a !== void 0 ? _a : this._names = this._items.reduce((names, c) => {
	      if (c instanceof Name) names[c.str] = (names[c.str] || 0) + 1;
	      return names;
	    }, {});
	  }
	}
	exports._Code = _Code;
	exports.nil = new _Code("");
	function _(strs, ...args) {
	  const code = [strs[0]];
	  let i = 0;
	  while (i < args.length) {
	    addCodeArg(code, args[i]);
	    code.push(strs[++i]);
	  }
	  return new _Code(code);
	}
	exports._ = _;
	const plus = new _Code("+");
	function str(strs, ...args) {
	  const expr = [safeStringify(strs[0])];
	  let i = 0;
	  while (i < args.length) {
	    expr.push(plus);
	    addCodeArg(expr, args[i]);
	    expr.push(plus, safeStringify(strs[++i]));
	  }
	  optimize(expr);
	  return new _Code(expr);
	}
	exports.str = str;
	function addCodeArg(code, arg) {
	  if (arg instanceof _Code) code.push(...arg._items);else if (arg instanceof Name) code.push(arg);else code.push(interpolate(arg));
	}
	exports.addCodeArg = addCodeArg;
	function optimize(expr) {
	  let i = 1;
	  while (i < expr.length - 1) {
	    if (expr[i] === plus) {
	      const res = mergeExprItems(expr[i - 1], expr[i + 1]);
	      if (res !== undefined) {
	        expr.splice(i - 1, 3, res);
	        continue;
	      }
	      expr[i++] = "+";
	    }
	    i++;
	  }
	}
	function mergeExprItems(a, b) {
	  if (b === '""') return a;
	  if (a === '""') return b;
	  if (typeof a == "string") {
	    if (b instanceof Name || a[a.length - 1] !== '"') return;
	    if (typeof b != "string") return `${a.slice(0, -1)}${b}"`;
	    if (b[0] === '"') return a.slice(0, -1) + b.slice(1);
	    return;
	  }
	  if (typeof b == "string" && b[0] === '"' && !(a instanceof Name)) return `"${a}${b.slice(1)}`;
	  return;
	}
	function strConcat(c1, c2) {
	  return c2.emptyStr() ? c1 : c1.emptyStr() ? c2 : str`${c1}${c2}`;
	}
	exports.strConcat = strConcat;
	// TODO do not allow arrays here
	function interpolate(x) {
	  return typeof x == "number" || typeof x == "boolean" || x === null ? x : safeStringify(Array.isArray(x) ? x.join(",") : x);
	}
	function stringify(x) {
	  return new _Code(safeStringify(x));
	}
	exports.stringify = stringify;
	function safeStringify(x) {
	  return JSON.stringify(x).replace(/\u2028/g, "\\u2028").replace(/\u2029/g, "\\u2029");
	}
	exports.safeStringify = safeStringify;
	function getProperty(key) {
	  return typeof key == "string" && exports.IDENTIFIER.test(key) ? new _Code(`.${key}`) : _`[${key}]`;
	}
	exports.getProperty = getProperty;
	//Does best effort to format the name properly
	function getEsmExportName(key) {
	  if (typeof key == "string" && exports.IDENTIFIER.test(key)) {
	    return new _Code(`${key}`);
	  }
	  throw new Error(`CodeGen: invalid export name: ${key}, use explicit $id name mapping`);
	}
	exports.getEsmExportName = getEsmExportName;
	function regexpCode(rx) {
	  return new _Code(rx.toString());
	}
	exports.regexpCode = regexpCode; 
} (code$1));

var scope = {};

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.ValueScope = exports.ValueScopeName = exports.Scope = exports.varKinds = exports.UsedValueState = void 0;
	const code_1 = code$1;
	class ValueError extends Error {
	  constructor(name) {
	    super(`CodeGen: "code" for ${name} not defined`);
	    this.value = name.value;
	  }
	}
	var UsedValueState;
	(function (UsedValueState) {
	  UsedValueState[UsedValueState["Started"] = 0] = "Started";
	  UsedValueState[UsedValueState["Completed"] = 1] = "Completed";
	})(UsedValueState || (exports.UsedValueState = UsedValueState = {}));
	exports.varKinds = {
	  const: new code_1.Name("const"),
	  let: new code_1.Name("let"),
	  var: new code_1.Name("var")
	};
	class Scope {
	  constructor({
	    prefixes,
	    parent
	  } = {}) {
	    this._names = {};
	    this._prefixes = prefixes;
	    this._parent = parent;
	  }
	  toName(nameOrPrefix) {
	    return nameOrPrefix instanceof code_1.Name ? nameOrPrefix : this.name(nameOrPrefix);
	  }
	  name(prefix) {
	    return new code_1.Name(this._newName(prefix));
	  }
	  _newName(prefix) {
	    const ng = this._names[prefix] || this._nameGroup(prefix);
	    return `${prefix}${ng.index++}`;
	  }
	  _nameGroup(prefix) {
	    var _a, _b;
	    if (((_b = (_a = this._parent) === null || _a === void 0 ? void 0 : _a._prefixes) === null || _b === void 0 ? void 0 : _b.has(prefix)) || this._prefixes && !this._prefixes.has(prefix)) {
	      throw new Error(`CodeGen: prefix "${prefix}" is not allowed in this scope`);
	    }
	    return this._names[prefix] = {
	      prefix,
	      index: 0
	    };
	  }
	}
	exports.Scope = Scope;
	class ValueScopeName extends code_1.Name {
	  constructor(prefix, nameStr) {
	    super(nameStr);
	    this.prefix = prefix;
	  }
	  setValue(value, {
	    property,
	    itemIndex
	  }) {
	    this.value = value;
	    this.scopePath = (0, code_1._)`.${new code_1.Name(property)}[${itemIndex}]`;
	  }
	}
	exports.ValueScopeName = ValueScopeName;
	const line = (0, code_1._)`\n`;
	class ValueScope extends Scope {
	  constructor(opts) {
	    super(opts);
	    this._values = {};
	    this._scope = opts.scope;
	    this.opts = {
	      ...opts,
	      _n: opts.lines ? line : code_1.nil
	    };
	  }
	  get() {
	    return this._scope;
	  }
	  name(prefix) {
	    return new ValueScopeName(prefix, this._newName(prefix));
	  }
	  value(nameOrPrefix, value) {
	    var _a;
	    if (value.ref === undefined) throw new Error("CodeGen: ref must be passed in value");
	    const name = this.toName(nameOrPrefix);
	    const {
	      prefix
	    } = name;
	    const valueKey = (_a = value.key) !== null && _a !== void 0 ? _a : value.ref;
	    let vs = this._values[prefix];
	    if (vs) {
	      const _name = vs.get(valueKey);
	      if (_name) return _name;
	    } else {
	      vs = this._values[prefix] = new Map();
	    }
	    vs.set(valueKey, name);
	    const s = this._scope[prefix] || (this._scope[prefix] = []);
	    const itemIndex = s.length;
	    s[itemIndex] = value.ref;
	    name.setValue(value, {
	      property: prefix,
	      itemIndex
	    });
	    return name;
	  }
	  getValue(prefix, keyOrRef) {
	    const vs = this._values[prefix];
	    if (!vs) return;
	    return vs.get(keyOrRef);
	  }
	  scopeRefs(scopeName, values = this._values) {
	    return this._reduceValues(values, name => {
	      if (name.scopePath === undefined) throw new Error(`CodeGen: name "${name}" has no value`);
	      return (0, code_1._)`${scopeName}${name.scopePath}`;
	    });
	  }
	  scopeCode(values = this._values, usedValues, getCode) {
	    return this._reduceValues(values, name => {
	      if (name.value === undefined) throw new Error(`CodeGen: name "${name}" has no value`);
	      return name.value.code;
	    }, usedValues, getCode);
	  }
	  _reduceValues(values, valueCode, usedValues = {}, getCode) {
	    let code = code_1.nil;
	    for (const prefix in values) {
	      const vs = values[prefix];
	      if (!vs) continue;
	      const nameSet = usedValues[prefix] = usedValues[prefix] || new Map();
	      vs.forEach(name => {
	        if (nameSet.has(name)) return;
	        nameSet.set(name, UsedValueState.Started);
	        let c = valueCode(name);
	        if (c) {
	          const def = this.opts.es5 ? exports.varKinds.var : exports.varKinds.const;
	          code = (0, code_1._)`${code}${def} ${name} = ${c};${this.opts._n}`;
	        } else if (c = getCode === null || getCode === void 0 ? void 0 : getCode(name)) {
	          code = (0, code_1._)`${code}${c}${this.opts._n}`;
	        } else {
	          throw new ValueError(name);
	        }
	        nameSet.set(name, UsedValueState.Completed);
	      });
	    }
	    return code;
	  }
	}
	exports.ValueScope = ValueScope; 
} (scope));

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.or = exports.and = exports.not = exports.CodeGen = exports.operators = exports.varKinds = exports.ValueScopeName = exports.ValueScope = exports.Scope = exports.Name = exports.regexpCode = exports.stringify = exports.getProperty = exports.nil = exports.strConcat = exports.str = exports._ = void 0;
	const code_1 = code$1;
	const scope_1 = scope;
	var code_2 = code$1;
	Object.defineProperty(exports, "_", {
	  enumerable: true,
	  get: function () {
	    return code_2._;
	  }
	});
	Object.defineProperty(exports, "str", {
	  enumerable: true,
	  get: function () {
	    return code_2.str;
	  }
	});
	Object.defineProperty(exports, "strConcat", {
	  enumerable: true,
	  get: function () {
	    return code_2.strConcat;
	  }
	});
	Object.defineProperty(exports, "nil", {
	  enumerable: true,
	  get: function () {
	    return code_2.nil;
	  }
	});
	Object.defineProperty(exports, "getProperty", {
	  enumerable: true,
	  get: function () {
	    return code_2.getProperty;
	  }
	});
	Object.defineProperty(exports, "stringify", {
	  enumerable: true,
	  get: function () {
	    return code_2.stringify;
	  }
	});
	Object.defineProperty(exports, "regexpCode", {
	  enumerable: true,
	  get: function () {
	    return code_2.regexpCode;
	  }
	});
	Object.defineProperty(exports, "Name", {
	  enumerable: true,
	  get: function () {
	    return code_2.Name;
	  }
	});
	var scope_2 = scope;
	Object.defineProperty(exports, "Scope", {
	  enumerable: true,
	  get: function () {
	    return scope_2.Scope;
	  }
	});
	Object.defineProperty(exports, "ValueScope", {
	  enumerable: true,
	  get: function () {
	    return scope_2.ValueScope;
	  }
	});
	Object.defineProperty(exports, "ValueScopeName", {
	  enumerable: true,
	  get: function () {
	    return scope_2.ValueScopeName;
	  }
	});
	Object.defineProperty(exports, "varKinds", {
	  enumerable: true,
	  get: function () {
	    return scope_2.varKinds;
	  }
	});
	exports.operators = {
	  GT: new code_1._Code(">"),
	  GTE: new code_1._Code(">="),
	  LT: new code_1._Code("<"),
	  LTE: new code_1._Code("<="),
	  EQ: new code_1._Code("==="),
	  NEQ: new code_1._Code("!=="),
	  NOT: new code_1._Code("!"),
	  OR: new code_1._Code("||"),
	  AND: new code_1._Code("&&"),
	  ADD: new code_1._Code("+")
	};
	class Node {
	  optimizeNodes() {
	    return this;
	  }
	  optimizeNames(_names, _constants) {
	    return this;
	  }
	}
	class Def extends Node {
	  constructor(varKind, name, rhs) {
	    super();
	    this.varKind = varKind;
	    this.name = name;
	    this.rhs = rhs;
	  }
	  render({
	    es5,
	    _n
	  }) {
	    const varKind = es5 ? scope_1.varKinds.var : this.varKind;
	    const rhs = this.rhs === undefined ? "" : ` = ${this.rhs}`;
	    return `${varKind} ${this.name}${rhs};` + _n;
	  }
	  optimizeNames(names, constants) {
	    if (!names[this.name.str]) return;
	    if (this.rhs) this.rhs = optimizeExpr(this.rhs, names, constants);
	    return this;
	  }
	  get names() {
	    return this.rhs instanceof code_1._CodeOrName ? this.rhs.names : {};
	  }
	}
	class Assign extends Node {
	  constructor(lhs, rhs, sideEffects) {
	    super();
	    this.lhs = lhs;
	    this.rhs = rhs;
	    this.sideEffects = sideEffects;
	  }
	  render({
	    _n
	  }) {
	    return `${this.lhs} = ${this.rhs};` + _n;
	  }
	  optimizeNames(names, constants) {
	    if (this.lhs instanceof code_1.Name && !names[this.lhs.str] && !this.sideEffects) return;
	    this.rhs = optimizeExpr(this.rhs, names, constants);
	    return this;
	  }
	  get names() {
	    const names = this.lhs instanceof code_1.Name ? {} : {
	      ...this.lhs.names
	    };
	    return addExprNames(names, this.rhs);
	  }
	}
	class AssignOp extends Assign {
	  constructor(lhs, op, rhs, sideEffects) {
	    super(lhs, rhs, sideEffects);
	    this.op = op;
	  }
	  render({
	    _n
	  }) {
	    return `${this.lhs} ${this.op}= ${this.rhs};` + _n;
	  }
	}
	class Label extends Node {
	  constructor(label) {
	    super();
	    this.label = label;
	    this.names = {};
	  }
	  render({
	    _n
	  }) {
	    return `${this.label}:` + _n;
	  }
	}
	class Break extends Node {
	  constructor(label) {
	    super();
	    this.label = label;
	    this.names = {};
	  }
	  render({
	    _n
	  }) {
	    const label = this.label ? ` ${this.label}` : "";
	    return `break${label};` + _n;
	  }
	}
	class Throw extends Node {
	  constructor(error) {
	    super();
	    this.error = error;
	  }
	  render({
	    _n
	  }) {
	    return `throw ${this.error};` + _n;
	  }
	  get names() {
	    return this.error.names;
	  }
	}
	class AnyCode extends Node {
	  constructor(code) {
	    super();
	    this.code = code;
	  }
	  render({
	    _n
	  }) {
	    return `${this.code};` + _n;
	  }
	  optimizeNodes() {
	    return `${this.code}` ? this : undefined;
	  }
	  optimizeNames(names, constants) {
	    this.code = optimizeExpr(this.code, names, constants);
	    return this;
	  }
	  get names() {
	    return this.code instanceof code_1._CodeOrName ? this.code.names : {};
	  }
	}
	class ParentNode extends Node {
	  constructor(nodes = []) {
	    super();
	    this.nodes = nodes;
	  }
	  render(opts) {
	    return this.nodes.reduce((code, n) => code + n.render(opts), "");
	  }
	  optimizeNodes() {
	    const {
	      nodes
	    } = this;
	    let i = nodes.length;
	    while (i--) {
	      const n = nodes[i].optimizeNodes();
	      if (Array.isArray(n)) nodes.splice(i, 1, ...n);else if (n) nodes[i] = n;else nodes.splice(i, 1);
	    }
	    return nodes.length > 0 ? this : undefined;
	  }
	  optimizeNames(names, constants) {
	    const {
	      nodes
	    } = this;
	    let i = nodes.length;
	    while (i--) {
	      // iterating backwards improves 1-pass optimization
	      const n = nodes[i];
	      if (n.optimizeNames(names, constants)) continue;
	      subtractNames(names, n.names);
	      nodes.splice(i, 1);
	    }
	    return nodes.length > 0 ? this : undefined;
	  }
	  get names() {
	    return this.nodes.reduce((names, n) => addNames(names, n.names), {});
	  }
	}
	class BlockNode extends ParentNode {
	  render(opts) {
	    return "{" + opts._n + super.render(opts) + "}" + opts._n;
	  }
	}
	class Root extends ParentNode {}
	class Else extends BlockNode {}
	Else.kind = "else";
	class If extends BlockNode {
	  constructor(condition, nodes) {
	    super(nodes);
	    this.condition = condition;
	  }
	  render(opts) {
	    let code = `if(${this.condition})` + super.render(opts);
	    if (this.else) code += "else " + this.else.render(opts);
	    return code;
	  }
	  optimizeNodes() {
	    super.optimizeNodes();
	    const cond = this.condition;
	    if (cond === true) return this.nodes; // else is ignored here
	    let e = this.else;
	    if (e) {
	      const ns = e.optimizeNodes();
	      e = this.else = Array.isArray(ns) ? new Else(ns) : ns;
	    }
	    if (e) {
	      if (cond === false) return e instanceof If ? e : e.nodes;
	      if (this.nodes.length) return this;
	      return new If(not(cond), e instanceof If ? [e] : e.nodes);
	    }
	    if (cond === false || !this.nodes.length) return undefined;
	    return this;
	  }
	  optimizeNames(names, constants) {
	    var _a;
	    this.else = (_a = this.else) === null || _a === void 0 ? void 0 : _a.optimizeNames(names, constants);
	    if (!(super.optimizeNames(names, constants) || this.else)) return;
	    this.condition = optimizeExpr(this.condition, names, constants);
	    return this;
	  }
	  get names() {
	    const names = super.names;
	    addExprNames(names, this.condition);
	    if (this.else) addNames(names, this.else.names);
	    return names;
	  }
	}
	If.kind = "if";
	class For extends BlockNode {}
	For.kind = "for";
	class ForLoop extends For {
	  constructor(iteration) {
	    super();
	    this.iteration = iteration;
	  }
	  render(opts) {
	    return `for(${this.iteration})` + super.render(opts);
	  }
	  optimizeNames(names, constants) {
	    if (!super.optimizeNames(names, constants)) return;
	    this.iteration = optimizeExpr(this.iteration, names, constants);
	    return this;
	  }
	  get names() {
	    return addNames(super.names, this.iteration.names);
	  }
	}
	class ForRange extends For {
	  constructor(varKind, name, from, to) {
	    super();
	    this.varKind = varKind;
	    this.name = name;
	    this.from = from;
	    this.to = to;
	  }
	  render(opts) {
	    const varKind = opts.es5 ? scope_1.varKinds.var : this.varKind;
	    const {
	      name,
	      from,
	      to
	    } = this;
	    return `for(${varKind} ${name}=${from}; ${name}<${to}; ${name}++)` + super.render(opts);
	  }
	  get names() {
	    const names = addExprNames(super.names, this.from);
	    return addExprNames(names, this.to);
	  }
	}
	class ForIter extends For {
	  constructor(loop, varKind, name, iterable) {
	    super();
	    this.loop = loop;
	    this.varKind = varKind;
	    this.name = name;
	    this.iterable = iterable;
	  }
	  render(opts) {
	    return `for(${this.varKind} ${this.name} ${this.loop} ${this.iterable})` + super.render(opts);
	  }
	  optimizeNames(names, constants) {
	    if (!super.optimizeNames(names, constants)) return;
	    this.iterable = optimizeExpr(this.iterable, names, constants);
	    return this;
	  }
	  get names() {
	    return addNames(super.names, this.iterable.names);
	  }
	}
	class Func extends BlockNode {
	  constructor(name, args, async) {
	    super();
	    this.name = name;
	    this.args = args;
	    this.async = async;
	  }
	  render(opts) {
	    const _async = this.async ? "async " : "";
	    return `${_async}function ${this.name}(${this.args})` + super.render(opts);
	  }
	}
	Func.kind = "func";
	class Return extends ParentNode {
	  render(opts) {
	    return "return " + super.render(opts);
	  }
	}
	Return.kind = "return";
	class Try extends BlockNode {
	  render(opts) {
	    let code = "try" + super.render(opts);
	    if (this.catch) code += this.catch.render(opts);
	    if (this.finally) code += this.finally.render(opts);
	    return code;
	  }
	  optimizeNodes() {
	    var _a, _b;
	    super.optimizeNodes();
	    (_a = this.catch) === null || _a === void 0 ? void 0 : _a.optimizeNodes();
	    (_b = this.finally) === null || _b === void 0 ? void 0 : _b.optimizeNodes();
	    return this;
	  }
	  optimizeNames(names, constants) {
	    var _a, _b;
	    super.optimizeNames(names, constants);
	    (_a = this.catch) === null || _a === void 0 ? void 0 : _a.optimizeNames(names, constants);
	    (_b = this.finally) === null || _b === void 0 ? void 0 : _b.optimizeNames(names, constants);
	    return this;
	  }
	  get names() {
	    const names = super.names;
	    if (this.catch) addNames(names, this.catch.names);
	    if (this.finally) addNames(names, this.finally.names);
	    return names;
	  }
	}
	class Catch extends BlockNode {
	  constructor(error) {
	    super();
	    this.error = error;
	  }
	  render(opts) {
	    return `catch(${this.error})` + super.render(opts);
	  }
	}
	Catch.kind = "catch";
	class Finally extends BlockNode {
	  render(opts) {
	    return "finally" + super.render(opts);
	  }
	}
	Finally.kind = "finally";
	class CodeGen {
	  constructor(extScope, opts = {}) {
	    this._values = {};
	    this._blockStarts = [];
	    this._constants = {};
	    this.opts = {
	      ...opts,
	      _n: opts.lines ? "\n" : ""
	    };
	    this._extScope = extScope;
	    this._scope = new scope_1.Scope({
	      parent: extScope
	    });
	    this._nodes = [new Root()];
	  }
	  toString() {
	    return this._root.render(this.opts);
	  }
	  // returns unique name in the internal scope
	  name(prefix) {
	    return this._scope.name(prefix);
	  }
	  // reserves unique name in the external scope
	  scopeName(prefix) {
	    return this._extScope.name(prefix);
	  }
	  // reserves unique name in the external scope and assigns value to it
	  scopeValue(prefixOrName, value) {
	    const name = this._extScope.value(prefixOrName, value);
	    const vs = this._values[name.prefix] || (this._values[name.prefix] = new Set());
	    vs.add(name);
	    return name;
	  }
	  getScopeValue(prefix, keyOrRef) {
	    return this._extScope.getValue(prefix, keyOrRef);
	  }
	  // return code that assigns values in the external scope to the names that are used internally
	  // (same names that were returned by gen.scopeName or gen.scopeValue)
	  scopeRefs(scopeName) {
	    return this._extScope.scopeRefs(scopeName, this._values);
	  }
	  scopeCode() {
	    return this._extScope.scopeCode(this._values);
	  }
	  _def(varKind, nameOrPrefix, rhs, constant) {
	    const name = this._scope.toName(nameOrPrefix);
	    if (rhs !== undefined && constant) this._constants[name.str] = rhs;
	    this._leafNode(new Def(varKind, name, rhs));
	    return name;
	  }
	  // `const` declaration (`var` in es5 mode)
	  const(nameOrPrefix, rhs, _constant) {
	    return this._def(scope_1.varKinds.const, nameOrPrefix, rhs, _constant);
	  }
	  // `let` declaration with optional assignment (`var` in es5 mode)
	  let(nameOrPrefix, rhs, _constant) {
	    return this._def(scope_1.varKinds.let, nameOrPrefix, rhs, _constant);
	  }
	  // `var` declaration with optional assignment
	  var(nameOrPrefix, rhs, _constant) {
	    return this._def(scope_1.varKinds.var, nameOrPrefix, rhs, _constant);
	  }
	  // assignment code
	  assign(lhs, rhs, sideEffects) {
	    return this._leafNode(new Assign(lhs, rhs, sideEffects));
	  }
	  // `+=` code
	  add(lhs, rhs) {
	    return this._leafNode(new AssignOp(lhs, exports.operators.ADD, rhs));
	  }
	  // appends passed SafeExpr to code or executes Block
	  code(c) {
	    if (typeof c == "function") c();else if (c !== code_1.nil) this._leafNode(new AnyCode(c));
	    return this;
	  }
	  // returns code for object literal for the passed argument list of key-value pairs
	  object(...keyValues) {
	    const code = ["{"];
	    for (const [key, value] of keyValues) {
	      if (code.length > 1) code.push(",");
	      code.push(key);
	      if (key !== value || this.opts.es5) {
	        code.push(":");
	        (0, code_1.addCodeArg)(code, value);
	      }
	    }
	    code.push("}");
	    return new code_1._Code(code);
	  }
	  // `if` clause (or statement if `thenBody` and, optionally, `elseBody` are passed)
	  if(condition, thenBody, elseBody) {
	    this._blockNode(new If(condition));
	    if (thenBody && elseBody) {
	      this.code(thenBody).else().code(elseBody).endIf();
	    } else if (thenBody) {
	      this.code(thenBody).endIf();
	    } else if (elseBody) {
	      throw new Error('CodeGen: "else" body without "then" body');
	    }
	    return this;
	  }
	  // `else if` clause - invalid without `if` or after `else` clauses
	  elseIf(condition) {
	    return this._elseNode(new If(condition));
	  }
	  // `else` clause - only valid after `if` or `else if` clauses
	  else() {
	    return this._elseNode(new Else());
	  }
	  // end `if` statement (needed if gen.if was used only with condition)
	  endIf() {
	    return this._endBlockNode(If, Else);
	  }
	  _for(node, forBody) {
	    this._blockNode(node);
	    if (forBody) this.code(forBody).endFor();
	    return this;
	  }
	  // a generic `for` clause (or statement if `forBody` is passed)
	  for(iteration, forBody) {
	    return this._for(new ForLoop(iteration), forBody);
	  }
	  // `for` statement for a range of values
	  forRange(nameOrPrefix, from, to, forBody, varKind = this.opts.es5 ? scope_1.varKinds.var : scope_1.varKinds.let) {
	    const name = this._scope.toName(nameOrPrefix);
	    return this._for(new ForRange(varKind, name, from, to), () => forBody(name));
	  }
	  // `for-of` statement (in es5 mode replace with a normal for loop)
	  forOf(nameOrPrefix, iterable, forBody, varKind = scope_1.varKinds.const) {
	    const name = this._scope.toName(nameOrPrefix);
	    if (this.opts.es5) {
	      const arr = iterable instanceof code_1.Name ? iterable : this.var("_arr", iterable);
	      return this.forRange("_i", 0, (0, code_1._)`${arr}.length`, i => {
	        this.var(name, (0, code_1._)`${arr}[${i}]`);
	        forBody(name);
	      });
	    }
	    return this._for(new ForIter("of", varKind, name, iterable), () => forBody(name));
	  }
	  // `for-in` statement.
	  // With option `ownProperties` replaced with a `for-of` loop for object keys
	  forIn(nameOrPrefix, obj, forBody, varKind = this.opts.es5 ? scope_1.varKinds.var : scope_1.varKinds.const) {
	    if (this.opts.ownProperties) {
	      return this.forOf(nameOrPrefix, (0, code_1._)`Object.keys(${obj})`, forBody);
	    }
	    const name = this._scope.toName(nameOrPrefix);
	    return this._for(new ForIter("in", varKind, name, obj), () => forBody(name));
	  }
	  // end `for` loop
	  endFor() {
	    return this._endBlockNode(For);
	  }
	  // `label` statement
	  label(label) {
	    return this._leafNode(new Label(label));
	  }
	  // `break` statement
	  break(label) {
	    return this._leafNode(new Break(label));
	  }
	  // `return` statement
	  return(value) {
	    const node = new Return();
	    this._blockNode(node);
	    this.code(value);
	    if (node.nodes.length !== 1) throw new Error('CodeGen: "return" should have one node');
	    return this._endBlockNode(Return);
	  }
	  // `try` statement
	  try(tryBody, catchCode, finallyCode) {
	    if (!catchCode && !finallyCode) throw new Error('CodeGen: "try" without "catch" and "finally"');
	    const node = new Try();
	    this._blockNode(node);
	    this.code(tryBody);
	    if (catchCode) {
	      const error = this.name("e");
	      this._currNode = node.catch = new Catch(error);
	      catchCode(error);
	    }
	    if (finallyCode) {
	      this._currNode = node.finally = new Finally();
	      this.code(finallyCode);
	    }
	    return this._endBlockNode(Catch, Finally);
	  }
	  // `throw` statement
	  throw(error) {
	    return this._leafNode(new Throw(error));
	  }
	  // start self-balancing block
	  block(body, nodeCount) {
	    this._blockStarts.push(this._nodes.length);
	    if (body) this.code(body).endBlock(nodeCount);
	    return this;
	  }
	  // end the current self-balancing block
	  endBlock(nodeCount) {
	    const len = this._blockStarts.pop();
	    if (len === undefined) throw new Error("CodeGen: not in self-balancing block");
	    const toClose = this._nodes.length - len;
	    if (toClose < 0 || nodeCount !== undefined && toClose !== nodeCount) {
	      throw new Error(`CodeGen: wrong number of nodes: ${toClose} vs ${nodeCount} expected`);
	    }
	    this._nodes.length = len;
	    return this;
	  }
	  // `function` heading (or definition if funcBody is passed)
	  func(name, args = code_1.nil, async, funcBody) {
	    this._blockNode(new Func(name, args, async));
	    if (funcBody) this.code(funcBody).endFunc();
	    return this;
	  }
	  // end function definition
	  endFunc() {
	    return this._endBlockNode(Func);
	  }
	  optimize(n = 1) {
	    while (n-- > 0) {
	      this._root.optimizeNodes();
	      this._root.optimizeNames(this._root.names, this._constants);
	    }
	  }
	  _leafNode(node) {
	    this._currNode.nodes.push(node);
	    return this;
	  }
	  _blockNode(node) {
	    this._currNode.nodes.push(node);
	    this._nodes.push(node);
	  }
	  _endBlockNode(N1, N2) {
	    const n = this._currNode;
	    if (n instanceof N1 || N2 && n instanceof N2) {
	      this._nodes.pop();
	      return this;
	    }
	    throw new Error(`CodeGen: not in block "${N2 ? `${N1.kind}/${N2.kind}` : N1.kind}"`);
	  }
	  _elseNode(node) {
	    const n = this._currNode;
	    if (!(n instanceof If)) {
	      throw new Error('CodeGen: "else" without "if"');
	    }
	    this._currNode = n.else = node;
	    return this;
	  }
	  get _root() {
	    return this._nodes[0];
	  }
	  get _currNode() {
	    const ns = this._nodes;
	    return ns[ns.length - 1];
	  }
	  set _currNode(node) {
	    const ns = this._nodes;
	    ns[ns.length - 1] = node;
	  }
	}
	exports.CodeGen = CodeGen;
	function addNames(names, from) {
	  for (const n in from) names[n] = (names[n] || 0) + (from[n] || 0);
	  return names;
	}
	function addExprNames(names, from) {
	  return from instanceof code_1._CodeOrName ? addNames(names, from.names) : names;
	}
	function optimizeExpr(expr, names, constants) {
	  if (expr instanceof code_1.Name) return replaceName(expr);
	  if (!canOptimize(expr)) return expr;
	  return new code_1._Code(expr._items.reduce((items, c) => {
	    if (c instanceof code_1.Name) c = replaceName(c);
	    if (c instanceof code_1._Code) items.push(...c._items);else items.push(c);
	    return items;
	  }, []));
	  function replaceName(n) {
	    const c = constants[n.str];
	    if (c === undefined || names[n.str] !== 1) return n;
	    delete names[n.str];
	    return c;
	  }
	  function canOptimize(e) {
	    return e instanceof code_1._Code && e._items.some(c => c instanceof code_1.Name && names[c.str] === 1 && constants[c.str] !== undefined);
	  }
	}
	function subtractNames(names, from) {
	  for (const n in from) names[n] = (names[n] || 0) - (from[n] || 0);
	}
	function not(x) {
	  return typeof x == "boolean" || typeof x == "number" || x === null ? !x : (0, code_1._)`!${par(x)}`;
	}
	exports.not = not;
	const andCode = mappend(exports.operators.AND);
	// boolean AND (&&) expression with the passed arguments
	function and(...args) {
	  return args.reduce(andCode);
	}
	exports.and = and;
	const orCode = mappend(exports.operators.OR);
	// boolean OR (||) expression with the passed arguments
	function or(...args) {
	  return args.reduce(orCode);
	}
	exports.or = or;
	function mappend(op) {
	  return (x, y) => x === code_1.nil ? y : y === code_1.nil ? x : (0, code_1._)`${par(x)} ${op} ${par(y)}`;
	}
	function par(x) {
	  return x instanceof code_1.Name ? x : (0, code_1._)`(${x})`;
	} 
} (codegen));

var util = {};

Object.defineProperty(util, "__esModule", {
  value: true
});
util.checkStrictMode = util.getErrorPath = util.Type = util.useFunc = util.setEvaluated = util.evaluatedPropsToName = util.mergeEvaluated = util.eachItem = util.unescapeJsonPointer = util.escapeJsonPointer = util.escapeFragment = util.unescapeFragment = util.schemaRefOrVal = util.schemaHasRulesButRef = util.schemaHasRules = util.checkUnknownRules = util.alwaysValidSchema = util.toHash = void 0;
const codegen_1$v = codegen;
const code_1$a = code$1;
// TODO refactor to use Set
function toHash(arr) {
  const hash = {};
  for (const item of arr) hash[item] = true;
  return hash;
}
util.toHash = toHash;
function alwaysValidSchema(it, schema) {
  if (typeof schema == "boolean") return schema;
  if (Object.keys(schema).length === 0) return true;
  checkUnknownRules(it, schema);
  return !schemaHasRules(schema, it.self.RULES.all);
}
util.alwaysValidSchema = alwaysValidSchema;
function checkUnknownRules(it, schema = it.schema) {
  const {
    opts,
    self
  } = it;
  if (!opts.strictSchema) return;
  if (typeof schema === "boolean") return;
  const rules = self.RULES.keywords;
  for (const key in schema) {
    if (!rules[key]) checkStrictMode(it, `unknown keyword: "${key}"`);
  }
}
util.checkUnknownRules = checkUnknownRules;
function schemaHasRules(schema, rules) {
  if (typeof schema == "boolean") return !schema;
  for (const key in schema) if (rules[key]) return true;
  return false;
}
util.schemaHasRules = schemaHasRules;
function schemaHasRulesButRef(schema, RULES) {
  if (typeof schema == "boolean") return !schema;
  for (const key in schema) if (key !== "$ref" && RULES.all[key]) return true;
  return false;
}
util.schemaHasRulesButRef = schemaHasRulesButRef;
function schemaRefOrVal({
  topSchemaRef,
  schemaPath
}, schema, keyword, $data) {
  if (!$data) {
    if (typeof schema == "number" || typeof schema == "boolean") return schema;
    if (typeof schema == "string") return (0, codegen_1$v._)`${schema}`;
  }
  return (0, codegen_1$v._)`${topSchemaRef}${schemaPath}${(0, codegen_1$v.getProperty)(keyword)}`;
}
util.schemaRefOrVal = schemaRefOrVal;
function unescapeFragment(str) {
  return unescapeJsonPointer(decodeURIComponent(str));
}
util.unescapeFragment = unescapeFragment;
function escapeFragment(str) {
  return encodeURIComponent(escapeJsonPointer(str));
}
util.escapeFragment = escapeFragment;
function escapeJsonPointer(str) {
  if (typeof str == "number") return `${str}`;
  return str.replace(/~/g, "~0").replace(/\//g, "~1");
}
util.escapeJsonPointer = escapeJsonPointer;
function unescapeJsonPointer(str) {
  return str.replace(/~1/g, "/").replace(/~0/g, "~");
}
util.unescapeJsonPointer = unescapeJsonPointer;
function eachItem(xs, f) {
  if (Array.isArray(xs)) {
    for (const x of xs) f(x);
  } else {
    f(xs);
  }
}
util.eachItem = eachItem;
function makeMergeEvaluated({
  mergeNames,
  mergeToName,
  mergeValues,
  resultToName
}) {
  return (gen, from, to, toName) => {
    const res = to === undefined ? from : to instanceof codegen_1$v.Name ? (from instanceof codegen_1$v.Name ? mergeNames(gen, from, to) : mergeToName(gen, from, to), to) : from instanceof codegen_1$v.Name ? (mergeToName(gen, to, from), from) : mergeValues(from, to);
    return toName === codegen_1$v.Name && !(res instanceof codegen_1$v.Name) ? resultToName(gen, res) : res;
  };
}
util.mergeEvaluated = {
  props: makeMergeEvaluated({
    mergeNames: (gen, from, to) => gen.if((0, codegen_1$v._)`${to} !== true && ${from} !== undefined`, () => {
      gen.if((0, codegen_1$v._)`${from} === true`, () => gen.assign(to, true), () => gen.assign(to, (0, codegen_1$v._)`${to} || {}`).code((0, codegen_1$v._)`Object.assign(${to}, ${from})`));
    }),
    mergeToName: (gen, from, to) => gen.if((0, codegen_1$v._)`${to} !== true`, () => {
      if (from === true) {
        gen.assign(to, true);
      } else {
        gen.assign(to, (0, codegen_1$v._)`${to} || {}`);
        setEvaluated(gen, to, from);
      }
    }),
    mergeValues: (from, to) => from === true ? true : {
      ...from,
      ...to
    },
    resultToName: evaluatedPropsToName
  }),
  items: makeMergeEvaluated({
    mergeNames: (gen, from, to) => gen.if((0, codegen_1$v._)`${to} !== true && ${from} !== undefined`, () => gen.assign(to, (0, codegen_1$v._)`${from} === true ? true : ${to} > ${from} ? ${to} : ${from}`)),
    mergeToName: (gen, from, to) => gen.if((0, codegen_1$v._)`${to} !== true`, () => gen.assign(to, from === true ? true : (0, codegen_1$v._)`${to} > ${from} ? ${to} : ${from}`)),
    mergeValues: (from, to) => from === true ? true : Math.max(from, to),
    resultToName: (gen, items) => gen.var("items", items)
  })
};
function evaluatedPropsToName(gen, ps) {
  if (ps === true) return gen.var("props", true);
  const props = gen.var("props", (0, codegen_1$v._)`{}`);
  if (ps !== undefined) setEvaluated(gen, props, ps);
  return props;
}
util.evaluatedPropsToName = evaluatedPropsToName;
function setEvaluated(gen, props, ps) {
  Object.keys(ps).forEach(p => gen.assign((0, codegen_1$v._)`${props}${(0, codegen_1$v.getProperty)(p)}`, true));
}
util.setEvaluated = setEvaluated;
const snippets = {};
function useFunc(gen, f) {
  return gen.scopeValue("func", {
    ref: f,
    code: snippets[f.code] || (snippets[f.code] = new code_1$a._Code(f.code))
  });
}
util.useFunc = useFunc;
var Type;
(function (Type) {
  Type[Type["Num"] = 0] = "Num";
  Type[Type["Str"] = 1] = "Str";
})(Type || (util.Type = Type = {}));
function getErrorPath(dataProp, dataPropType, jsPropertySyntax) {
  // let path
  if (dataProp instanceof codegen_1$v.Name) {
    const isNumber = dataPropType === Type.Num;
    return jsPropertySyntax ? isNumber ? (0, codegen_1$v._)`"[" + ${dataProp} + "]"` : (0, codegen_1$v._)`"['" + ${dataProp} + "']"` : isNumber ? (0, codegen_1$v._)`"/" + ${dataProp}` : (0, codegen_1$v._)`"/" + ${dataProp}.replace(/~/g, "~0").replace(/\\//g, "~1")`; // TODO maybe use global escapePointer
  }
  return jsPropertySyntax ? (0, codegen_1$v.getProperty)(dataProp).toString() : "/" + escapeJsonPointer(dataProp);
}
util.getErrorPath = getErrorPath;
function checkStrictMode(it, msg, mode = it.opts.strictSchema) {
  if (!mode) return;
  msg = `strict mode: ${msg}`;
  if (mode === true) throw new Error(msg);
  it.self.logger.warn(msg);
}
util.checkStrictMode = checkStrictMode;

var names$1 = {};

Object.defineProperty(names$1, "__esModule", {
  value: true
});
const codegen_1$u = codegen;
const names = {
  // validation function arguments
  data: new codegen_1$u.Name("data"),
  // data passed to validation function
  // args passed from referencing schema
  valCxt: new codegen_1$u.Name("valCxt"),
  // validation/data context - should not be used directly, it is destructured to the names below
  instancePath: new codegen_1$u.Name("instancePath"),
  parentData: new codegen_1$u.Name("parentData"),
  parentDataProperty: new codegen_1$u.Name("parentDataProperty"),
  rootData: new codegen_1$u.Name("rootData"),
  // root data - same as the data passed to the first/top validation function
  dynamicAnchors: new codegen_1$u.Name("dynamicAnchors"),
  // used to support recursiveRef and dynamicRef
  // function scoped variables
  vErrors: new codegen_1$u.Name("vErrors"),
  // null or array of validation errors
  errors: new codegen_1$u.Name("errors"),
  // counter of validation errors
  this: new codegen_1$u.Name("this"),
  // "globals"
  self: new codegen_1$u.Name("self"),
  scope: new codegen_1$u.Name("scope"),
  // JTD serialize/parse name for JSON string and position
  json: new codegen_1$u.Name("json"),
  jsonPos: new codegen_1$u.Name("jsonPos"),
  jsonLen: new codegen_1$u.Name("jsonLen"),
  jsonPart: new codegen_1$u.Name("jsonPart")
};
names$1.default = names;

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.extendErrors = exports.resetErrorsCount = exports.reportExtraError = exports.reportError = exports.keyword$DataError = exports.keywordError = void 0;
	const codegen_1 = codegen;
	const util_1 = util;
	const names_1 = names$1;
	exports.keywordError = {
	  message: ({
	    keyword
	  }) => (0, codegen_1.str)`must pass "${keyword}" keyword validation`
	};
	exports.keyword$DataError = {
	  message: ({
	    keyword,
	    schemaType
	  }) => schemaType ? (0, codegen_1.str)`"${keyword}" keyword must be ${schemaType} ($data)` : (0, codegen_1.str)`"${keyword}" keyword is invalid ($data)`
	};
	function reportError(cxt, error = exports.keywordError, errorPaths, overrideAllErrors) {
	  const {
	    it
	  } = cxt;
	  const {
	    gen,
	    compositeRule,
	    allErrors
	  } = it;
	  const errObj = errorObjectCode(cxt, error, errorPaths);
	  if (overrideAllErrors !== null && overrideAllErrors !== void 0 ? overrideAllErrors : compositeRule || allErrors) {
	    addError(gen, errObj);
	  } else {
	    returnErrors(it, (0, codegen_1._)`[${errObj}]`);
	  }
	}
	exports.reportError = reportError;
	function reportExtraError(cxt, error = exports.keywordError, errorPaths) {
	  const {
	    it
	  } = cxt;
	  const {
	    gen,
	    compositeRule,
	    allErrors
	  } = it;
	  const errObj = errorObjectCode(cxt, error, errorPaths);
	  addError(gen, errObj);
	  if (!(compositeRule || allErrors)) {
	    returnErrors(it, names_1.default.vErrors);
	  }
	}
	exports.reportExtraError = reportExtraError;
	function resetErrorsCount(gen, errsCount) {
	  gen.assign(names_1.default.errors, errsCount);
	  gen.if((0, codegen_1._)`${names_1.default.vErrors} !== null`, () => gen.if(errsCount, () => gen.assign((0, codegen_1._)`${names_1.default.vErrors}.length`, errsCount), () => gen.assign(names_1.default.vErrors, null)));
	}
	exports.resetErrorsCount = resetErrorsCount;
	function extendErrors({
	  gen,
	  keyword,
	  schemaValue,
	  data,
	  errsCount,
	  it
	}) {
	  /* istanbul ignore if */
	  if (errsCount === undefined) throw new Error("ajv implementation error");
	  const err = gen.name("err");
	  gen.forRange("i", errsCount, names_1.default.errors, i => {
	    gen.const(err, (0, codegen_1._)`${names_1.default.vErrors}[${i}]`);
	    gen.if((0, codegen_1._)`${err}.instancePath === undefined`, () => gen.assign((0, codegen_1._)`${err}.instancePath`, (0, codegen_1.strConcat)(names_1.default.instancePath, it.errorPath)));
	    gen.assign((0, codegen_1._)`${err}.schemaPath`, (0, codegen_1.str)`${it.errSchemaPath}/${keyword}`);
	    if (it.opts.verbose) {
	      gen.assign((0, codegen_1._)`${err}.schema`, schemaValue);
	      gen.assign((0, codegen_1._)`${err}.data`, data);
	    }
	  });
	}
	exports.extendErrors = extendErrors;
	function addError(gen, errObj) {
	  const err = gen.const("err", errObj);
	  gen.if((0, codegen_1._)`${names_1.default.vErrors} === null`, () => gen.assign(names_1.default.vErrors, (0, codegen_1._)`[${err}]`), (0, codegen_1._)`${names_1.default.vErrors}.push(${err})`);
	  gen.code((0, codegen_1._)`${names_1.default.errors}++`);
	}
	function returnErrors(it, errs) {
	  const {
	    gen,
	    validateName,
	    schemaEnv
	  } = it;
	  if (schemaEnv.$async) {
	    gen.throw((0, codegen_1._)`new ${it.ValidationError}(${errs})`);
	  } else {
	    gen.assign((0, codegen_1._)`${validateName}.errors`, errs);
	    gen.return(false);
	  }
	}
	const E = {
	  keyword: new codegen_1.Name("keyword"),
	  schemaPath: new codegen_1.Name("schemaPath"),
	  // also used in JTD errors
	  params: new codegen_1.Name("params"),
	  propertyName: new codegen_1.Name("propertyName"),
	  message: new codegen_1.Name("message"),
	  schema: new codegen_1.Name("schema"),
	  parentSchema: new codegen_1.Name("parentSchema")
	};
	function errorObjectCode(cxt, error, errorPaths) {
	  const {
	    createErrors
	  } = cxt.it;
	  if (createErrors === false) return (0, codegen_1._)`{}`;
	  return errorObject(cxt, error, errorPaths);
	}
	function errorObject(cxt, error, errorPaths = {}) {
	  const {
	    gen,
	    it
	  } = cxt;
	  const keyValues = [errorInstancePath(it, errorPaths), errorSchemaPath(cxt, errorPaths)];
	  extraErrorProps(cxt, error, keyValues);
	  return gen.object(...keyValues);
	}
	function errorInstancePath({
	  errorPath
	}, {
	  instancePath
	}) {
	  const instPath = instancePath ? (0, codegen_1.str)`${errorPath}${(0, util_1.getErrorPath)(instancePath, util_1.Type.Str)}` : errorPath;
	  return [names_1.default.instancePath, (0, codegen_1.strConcat)(names_1.default.instancePath, instPath)];
	}
	function errorSchemaPath({
	  keyword,
	  it: {
	    errSchemaPath
	  }
	}, {
	  schemaPath,
	  parentSchema
	}) {
	  let schPath = parentSchema ? errSchemaPath : (0, codegen_1.str)`${errSchemaPath}/${keyword}`;
	  if (schemaPath) {
	    schPath = (0, codegen_1.str)`${schPath}${(0, util_1.getErrorPath)(schemaPath, util_1.Type.Str)}`;
	  }
	  return [E.schemaPath, schPath];
	}
	function extraErrorProps(cxt, {
	  params,
	  message
	}, keyValues) {
	  const {
	    keyword,
	    data,
	    schemaValue,
	    it
	  } = cxt;
	  const {
	    opts,
	    propertyName,
	    topSchemaRef,
	    schemaPath
	  } = it;
	  keyValues.push([E.keyword, keyword], [E.params, typeof params == "function" ? params(cxt) : params || (0, codegen_1._)`{}`]);
	  if (opts.messages) {
	    keyValues.push([E.message, typeof message == "function" ? message(cxt) : message]);
	  }
	  if (opts.verbose) {
	    keyValues.push([E.schema, schemaValue], [E.parentSchema, (0, codegen_1._)`${topSchemaRef}${schemaPath}`], [names_1.default.data, data]);
	  }
	  if (propertyName) keyValues.push([E.propertyName, propertyName]);
	} 
} (errors));

Object.defineProperty(boolSchema, "__esModule", {
  value: true
});
boolSchema.boolOrEmptySchema = boolSchema.topBoolOrEmptySchema = void 0;
const errors_1$3 = errors;
const codegen_1$t = codegen;
const names_1$6 = names$1;
const boolError = {
  message: "boolean schema is false"
};
function topBoolOrEmptySchema(it) {
  const {
    gen,
    schema,
    validateName
  } = it;
  if (schema === false) {
    falseSchemaError(it, false);
  } else if (typeof schema == "object" && schema.$async === true) {
    gen.return(names_1$6.default.data);
  } else {
    gen.assign((0, codegen_1$t._)`${validateName}.errors`, null);
    gen.return(true);
  }
}
boolSchema.topBoolOrEmptySchema = topBoolOrEmptySchema;
function boolOrEmptySchema(it, valid) {
  const {
    gen,
    schema
  } = it;
  if (schema === false) {
    gen.var(valid, false); // TODO var
    falseSchemaError(it);
  } else {
    gen.var(valid, true); // TODO var
  }
}
boolSchema.boolOrEmptySchema = boolOrEmptySchema;
function falseSchemaError(it, overrideAllErrors) {
  const {
    gen,
    data
  } = it;
  // TODO maybe some other interface should be used for non-keyword validation errors...
  const cxt = {
    gen,
    keyword: "false schema",
    data,
    schema: false,
    schemaCode: false,
    schemaValue: false,
    params: {},
    it
  };
  (0, errors_1$3.reportError)(cxt, boolError, undefined, overrideAllErrors);
}

var dataType = {};

var rules = {};

Object.defineProperty(rules, "__esModule", {
  value: true
});
rules.getRules = rules.isJSONType = void 0;
const _jsonTypes = ["string", "number", "integer", "boolean", "null", "object", "array"];
const jsonTypes = new Set(_jsonTypes);
function isJSONType(x) {
  return typeof x == "string" && jsonTypes.has(x);
}
rules.isJSONType = isJSONType;
function getRules() {
  const groups = {
    number: {
      type: "number",
      rules: []
    },
    string: {
      type: "string",
      rules: []
    },
    array: {
      type: "array",
      rules: []
    },
    object: {
      type: "object",
      rules: []
    }
  };
  return {
    types: {
      ...groups,
      integer: true,
      boolean: true,
      null: true
    },
    rules: [{
      rules: []
    }, groups.number, groups.string, groups.array, groups.object],
    post: {
      rules: []
    },
    all: {},
    keywords: {}
  };
}
rules.getRules = getRules;

var applicability = {};

Object.defineProperty(applicability, "__esModule", {
  value: true
});
applicability.shouldUseRule = applicability.shouldUseGroup = applicability.schemaHasRulesForType = void 0;
function schemaHasRulesForType({
  schema,
  self
}, type) {
  const group = self.RULES.types[type];
  return group && group !== true && shouldUseGroup(schema, group);
}
applicability.schemaHasRulesForType = schemaHasRulesForType;
function shouldUseGroup(schema, group) {
  return group.rules.some(rule => shouldUseRule(schema, rule));
}
applicability.shouldUseGroup = shouldUseGroup;
function shouldUseRule(schema, rule) {
  var _a;
  return schema[rule.keyword] !== undefined || ((_a = rule.definition.implements) === null || _a === void 0 ? void 0 : _a.some(kwd => schema[kwd] !== undefined));
}
applicability.shouldUseRule = shouldUseRule;

Object.defineProperty(dataType, "__esModule", {
  value: true
});
dataType.reportTypeError = dataType.checkDataTypes = dataType.checkDataType = dataType.coerceAndCheckDataType = dataType.getJSONTypes = dataType.getSchemaTypes = dataType.DataType = void 0;
const rules_1 = rules;
const applicability_1$1 = applicability;
const errors_1$2 = errors;
const codegen_1$s = codegen;
const util_1$q = util;
var DataType;
(function (DataType) {
  DataType[DataType["Correct"] = 0] = "Correct";
  DataType[DataType["Wrong"] = 1] = "Wrong";
})(DataType || (dataType.DataType = DataType = {}));
function getSchemaTypes(schema) {
  const types = getJSONTypes(schema.type);
  const hasNull = types.includes("null");
  if (hasNull) {
    if (schema.nullable === false) throw new Error("type: null contradicts nullable: false");
  } else {
    if (!types.length && schema.nullable !== undefined) {
      throw new Error('"nullable" cannot be used without "type"');
    }
    if (schema.nullable === true) types.push("null");
  }
  return types;
}
dataType.getSchemaTypes = getSchemaTypes;
// eslint-disable-next-line @typescript-eslint/no-redundant-type-constituents
function getJSONTypes(ts) {
  const types = Array.isArray(ts) ? ts : ts ? [ts] : [];
  if (types.every(rules_1.isJSONType)) return types;
  throw new Error("type must be JSONType or JSONType[]: " + types.join(","));
}
dataType.getJSONTypes = getJSONTypes;
function coerceAndCheckDataType(it, types) {
  const {
    gen,
    data,
    opts
  } = it;
  const coerceTo = coerceToTypes(types, opts.coerceTypes);
  const checkTypes = types.length > 0 && !(coerceTo.length === 0 && types.length === 1 && (0, applicability_1$1.schemaHasRulesForType)(it, types[0]));
  if (checkTypes) {
    const wrongType = checkDataTypes(types, data, opts.strictNumbers, DataType.Wrong);
    gen.if(wrongType, () => {
      if (coerceTo.length) coerceData(it, types, coerceTo);else reportTypeError(it);
    });
  }
  return checkTypes;
}
dataType.coerceAndCheckDataType = coerceAndCheckDataType;
const COERCIBLE = new Set(["string", "number", "integer", "boolean", "null"]);
function coerceToTypes(types, coerceTypes) {
  return coerceTypes ? types.filter(t => COERCIBLE.has(t) || coerceTypes === "array" && t === "array") : [];
}
function coerceData(it, types, coerceTo) {
  const {
    gen,
    data,
    opts
  } = it;
  const dataType = gen.let("dataType", (0, codegen_1$s._)`typeof ${data}`);
  const coerced = gen.let("coerced", (0, codegen_1$s._)`undefined`);
  if (opts.coerceTypes === "array") {
    gen.if((0, codegen_1$s._)`${dataType} == 'object' && Array.isArray(${data}) && ${data}.length == 1`, () => gen.assign(data, (0, codegen_1$s._)`${data}[0]`).assign(dataType, (0, codegen_1$s._)`typeof ${data}`).if(checkDataTypes(types, data, opts.strictNumbers), () => gen.assign(coerced, data)));
  }
  gen.if((0, codegen_1$s._)`${coerced} !== undefined`);
  for (const t of coerceTo) {
    if (COERCIBLE.has(t) || t === "array" && opts.coerceTypes === "array") {
      coerceSpecificType(t);
    }
  }
  gen.else();
  reportTypeError(it);
  gen.endIf();
  gen.if((0, codegen_1$s._)`${coerced} !== undefined`, () => {
    gen.assign(data, coerced);
    assignParentData(it, coerced);
  });
  function coerceSpecificType(t) {
    switch (t) {
      case "string":
        gen.elseIf((0, codegen_1$s._)`${dataType} == "number" || ${dataType} == "boolean"`).assign(coerced, (0, codegen_1$s._)`"" + ${data}`).elseIf((0, codegen_1$s._)`${data} === null`).assign(coerced, (0, codegen_1$s._)`""`);
        return;
      case "number":
        gen.elseIf((0, codegen_1$s._)`${dataType} == "boolean" || ${data} === null
              || (${dataType} == "string" && ${data} && ${data} == +${data})`).assign(coerced, (0, codegen_1$s._)`+${data}`);
        return;
      case "integer":
        gen.elseIf((0, codegen_1$s._)`${dataType} === "boolean" || ${data} === null
              || (${dataType} === "string" && ${data} && ${data} == +${data} && !(${data} % 1))`).assign(coerced, (0, codegen_1$s._)`+${data}`);
        return;
      case "boolean":
        gen.elseIf((0, codegen_1$s._)`${data} === "false" || ${data} === 0 || ${data} === null`).assign(coerced, false).elseIf((0, codegen_1$s._)`${data} === "true" || ${data} === 1`).assign(coerced, true);
        return;
      case "null":
        gen.elseIf((0, codegen_1$s._)`${data} === "" || ${data} === 0 || ${data} === false`);
        gen.assign(coerced, null);
        return;
      case "array":
        gen.elseIf((0, codegen_1$s._)`${dataType} === "string" || ${dataType} === "number"
              || ${dataType} === "boolean" || ${data} === null`).assign(coerced, (0, codegen_1$s._)`[${data}]`);
    }
  }
}
function assignParentData({
  gen,
  parentData,
  parentDataProperty
}, expr) {
  // TODO use gen.property
  gen.if((0, codegen_1$s._)`${parentData} !== undefined`, () => gen.assign((0, codegen_1$s._)`${parentData}[${parentDataProperty}]`, expr));
}
function checkDataType(dataType, data, strictNums, correct = DataType.Correct) {
  const EQ = correct === DataType.Correct ? codegen_1$s.operators.EQ : codegen_1$s.operators.NEQ;
  let cond;
  switch (dataType) {
    case "null":
      return (0, codegen_1$s._)`${data} ${EQ} null`;
    case "array":
      cond = (0, codegen_1$s._)`Array.isArray(${data})`;
      break;
    case "object":
      cond = (0, codegen_1$s._)`${data} && typeof ${data} == "object" && !Array.isArray(${data})`;
      break;
    case "integer":
      cond = numCond((0, codegen_1$s._)`!(${data} % 1) && !isNaN(${data})`);
      break;
    case "number":
      cond = numCond();
      break;
    default:
      return (0, codegen_1$s._)`typeof ${data} ${EQ} ${dataType}`;
  }
  return correct === DataType.Correct ? cond : (0, codegen_1$s.not)(cond);
  function numCond(_cond = codegen_1$s.nil) {
    return (0, codegen_1$s.and)((0, codegen_1$s._)`typeof ${data} == "number"`, _cond, strictNums ? (0, codegen_1$s._)`isFinite(${data})` : codegen_1$s.nil);
  }
}
dataType.checkDataType = checkDataType;
function checkDataTypes(dataTypes, data, strictNums, correct) {
  if (dataTypes.length === 1) {
    return checkDataType(dataTypes[0], data, strictNums, correct);
  }
  let cond;
  const types = (0, util_1$q.toHash)(dataTypes);
  if (types.array && types.object) {
    const notObj = (0, codegen_1$s._)`typeof ${data} != "object"`;
    cond = types.null ? notObj : (0, codegen_1$s._)`!${data} || ${notObj}`;
    delete types.null;
    delete types.array;
    delete types.object;
  } else {
    cond = codegen_1$s.nil;
  }
  if (types.number) delete types.integer;
  for (const t in types) cond = (0, codegen_1$s.and)(cond, checkDataType(t, data, strictNums, correct));
  return cond;
}
dataType.checkDataTypes = checkDataTypes;
const typeError = {
  message: ({
    schema
  }) => `must be ${schema}`,
  params: ({
    schema,
    schemaValue
  }) => typeof schema == "string" ? (0, codegen_1$s._)`{type: ${schema}}` : (0, codegen_1$s._)`{type: ${schemaValue}}`
};
function reportTypeError(it) {
  const cxt = getTypeErrorContext(it);
  (0, errors_1$2.reportError)(cxt, typeError);
}
dataType.reportTypeError = reportTypeError;
function getTypeErrorContext(it) {
  const {
    gen,
    data,
    schema
  } = it;
  const schemaCode = (0, util_1$q.schemaRefOrVal)(it, schema, "type");
  return {
    gen,
    keyword: "type",
    data,
    schema: schema.type,
    schemaCode,
    schemaValue: schemaCode,
    parentSchema: schema,
    params: {},
    it
  };
}

var defaults = {};

Object.defineProperty(defaults, "__esModule", {
  value: true
});
defaults.assignDefaults = void 0;
const codegen_1$r = codegen;
const util_1$p = util;
function assignDefaults(it, ty) {
  const {
    properties,
    items
  } = it.schema;
  if (ty === "object" && properties) {
    for (const key in properties) {
      assignDefault(it, key, properties[key].default);
    }
  } else if (ty === "array" && Array.isArray(items)) {
    items.forEach((sch, i) => assignDefault(it, i, sch.default));
  }
}
defaults.assignDefaults = assignDefaults;
function assignDefault(it, prop, defaultValue) {
  const {
    gen,
    compositeRule,
    data,
    opts
  } = it;
  if (defaultValue === undefined) return;
  const childData = (0, codegen_1$r._)`${data}${(0, codegen_1$r.getProperty)(prop)}`;
  if (compositeRule) {
    (0, util_1$p.checkStrictMode)(it, `default is ignored for: ${childData}`);
    return;
  }
  let condition = (0, codegen_1$r._)`${childData} === undefined`;
  if (opts.useDefaults === "empty") {
    condition = (0, codegen_1$r._)`${condition} || ${childData} === null || ${childData} === ""`;
  }
  // `${childData} === undefined` +
  // (opts.useDefaults === "empty" ? ` || ${childData} === null || ${childData} === ""` : "")
  gen.if(condition, (0, codegen_1$r._)`${childData} = ${(0, codegen_1$r.stringify)(defaultValue)}`);
}

var keyword = {};

var code = {};

Object.defineProperty(code, "__esModule", {
  value: true
});
code.validateUnion = code.validateArray = code.usePattern = code.callValidateCode = code.schemaProperties = code.allSchemaProperties = code.noPropertyInData = code.propertyInData = code.isOwnProperty = code.hasPropFunc = code.reportMissingProp = code.checkMissingProp = code.checkReportMissingProp = void 0;
const codegen_1$q = codegen;
const util_1$o = util;
const names_1$5 = names$1;
const util_2$1 = util;
function checkReportMissingProp(cxt, prop) {
  const {
    gen,
    data,
    it
  } = cxt;
  gen.if(noPropertyInData(gen, data, prop, it.opts.ownProperties), () => {
    cxt.setParams({
      missingProperty: (0, codegen_1$q._)`${prop}`
    }, true);
    cxt.error();
  });
}
code.checkReportMissingProp = checkReportMissingProp;
function checkMissingProp({
  gen,
  data,
  it: {
    opts
  }
}, properties, missing) {
  return (0, codegen_1$q.or)(...properties.map(prop => (0, codegen_1$q.and)(noPropertyInData(gen, data, prop, opts.ownProperties), (0, codegen_1$q._)`${missing} = ${prop}`)));
}
code.checkMissingProp = checkMissingProp;
function reportMissingProp(cxt, missing) {
  cxt.setParams({
    missingProperty: missing
  }, true);
  cxt.error();
}
code.reportMissingProp = reportMissingProp;
function hasPropFunc(gen) {
  return gen.scopeValue("func", {
    // eslint-disable-next-line @typescript-eslint/unbound-method
    ref: Object.prototype.hasOwnProperty,
    code: (0, codegen_1$q._)`Object.prototype.hasOwnProperty`
  });
}
code.hasPropFunc = hasPropFunc;
function isOwnProperty(gen, data, property) {
  return (0, codegen_1$q._)`${hasPropFunc(gen)}.call(${data}, ${property})`;
}
code.isOwnProperty = isOwnProperty;
function propertyInData(gen, data, property, ownProperties) {
  const cond = (0, codegen_1$q._)`${data}${(0, codegen_1$q.getProperty)(property)} !== undefined`;
  return ownProperties ? (0, codegen_1$q._)`${cond} && ${isOwnProperty(gen, data, property)}` : cond;
}
code.propertyInData = propertyInData;
function noPropertyInData(gen, data, property, ownProperties) {
  const cond = (0, codegen_1$q._)`${data}${(0, codegen_1$q.getProperty)(property)} === undefined`;
  return ownProperties ? (0, codegen_1$q.or)(cond, (0, codegen_1$q.not)(isOwnProperty(gen, data, property))) : cond;
}
code.noPropertyInData = noPropertyInData;
function allSchemaProperties(schemaMap) {
  return schemaMap ? Object.keys(schemaMap).filter(p => p !== "__proto__") : [];
}
code.allSchemaProperties = allSchemaProperties;
function schemaProperties(it, schemaMap) {
  return allSchemaProperties(schemaMap).filter(p => !(0, util_1$o.alwaysValidSchema)(it, schemaMap[p]));
}
code.schemaProperties = schemaProperties;
function callValidateCode({
  schemaCode,
  data,
  it: {
    gen,
    topSchemaRef,
    schemaPath,
    errorPath
  },
  it
}, func, context, passSchema) {
  const dataAndSchema = passSchema ? (0, codegen_1$q._)`${schemaCode}, ${data}, ${topSchemaRef}${schemaPath}` : data;
  const valCxt = [[names_1$5.default.instancePath, (0, codegen_1$q.strConcat)(names_1$5.default.instancePath, errorPath)], [names_1$5.default.parentData, it.parentData], [names_1$5.default.parentDataProperty, it.parentDataProperty], [names_1$5.default.rootData, names_1$5.default.rootData]];
  if (it.opts.dynamicRef) valCxt.push([names_1$5.default.dynamicAnchors, names_1$5.default.dynamicAnchors]);
  const args = (0, codegen_1$q._)`${dataAndSchema}, ${gen.object(...valCxt)}`;
  return context !== codegen_1$q.nil ? (0, codegen_1$q._)`${func}.call(${context}, ${args})` : (0, codegen_1$q._)`${func}(${args})`;
}
code.callValidateCode = callValidateCode;
const newRegExp = (0, codegen_1$q._)`new RegExp`;
function usePattern({
  gen,
  it: {
    opts
  }
}, pattern) {
  const u = opts.unicodeRegExp ? "u" : "";
  const {
    regExp
  } = opts.code;
  const rx = regExp(pattern, u);
  return gen.scopeValue("pattern", {
    key: rx.toString(),
    ref: rx,
    code: (0, codegen_1$q._)`${regExp.code === "new RegExp" ? newRegExp : (0, util_2$1.useFunc)(gen, regExp)}(${pattern}, ${u})`
  });
}
code.usePattern = usePattern;
function validateArray(cxt) {
  const {
    gen,
    data,
    keyword,
    it
  } = cxt;
  const valid = gen.name("valid");
  if (it.allErrors) {
    const validArr = gen.let("valid", true);
    validateItems(() => gen.assign(validArr, false));
    return validArr;
  }
  gen.var(valid, true);
  validateItems(() => gen.break());
  return valid;
  function validateItems(notValid) {
    const len = gen.const("len", (0, codegen_1$q._)`${data}.length`);
    gen.forRange("i", 0, len, i => {
      cxt.subschema({
        keyword,
        dataProp: i,
        dataPropType: util_1$o.Type.Num
      }, valid);
      gen.if((0, codegen_1$q.not)(valid), notValid);
    });
  }
}
code.validateArray = validateArray;
function validateUnion(cxt) {
  const {
    gen,
    schema,
    keyword,
    it
  } = cxt;
  /* istanbul ignore if */
  if (!Array.isArray(schema)) throw new Error("ajv implementation error");
  const alwaysValid = schema.some(sch => (0, util_1$o.alwaysValidSchema)(it, sch));
  if (alwaysValid && !it.opts.unevaluated) return;
  const valid = gen.let("valid", false);
  const schValid = gen.name("_valid");
  gen.block(() => schema.forEach((_sch, i) => {
    const schCxt = cxt.subschema({
      keyword,
      schemaProp: i,
      compositeRule: true
    }, schValid);
    gen.assign(valid, (0, codegen_1$q._)`${valid} || ${schValid}`);
    const merged = cxt.mergeValidEvaluated(schCxt, schValid);
    // can short-circuit if `unevaluatedProperties/Items` not supported (opts.unevaluated !== true)
    // or if all properties and items were evaluated (it.props === true && it.items === true)
    if (!merged) gen.if((0, codegen_1$q.not)(valid));
  }));
  cxt.result(valid, () => cxt.reset(), () => cxt.error(true));
}
code.validateUnion = validateUnion;

Object.defineProperty(keyword, "__esModule", {
  value: true
});
keyword.validateKeywordUsage = keyword.validSchemaType = keyword.funcKeywordCode = keyword.macroKeywordCode = void 0;
const codegen_1$p = codegen;
const names_1$4 = names$1;
const code_1$9 = code;
const errors_1$1 = errors;
function macroKeywordCode(cxt, def) {
  const {
    gen,
    keyword,
    schema,
    parentSchema,
    it
  } = cxt;
  const macroSchema = def.macro.call(it.self, schema, parentSchema, it);
  const schemaRef = useKeyword(gen, keyword, macroSchema);
  if (it.opts.validateSchema !== false) it.self.validateSchema(macroSchema, true);
  const valid = gen.name("valid");
  cxt.subschema({
    schema: macroSchema,
    schemaPath: codegen_1$p.nil,
    errSchemaPath: `${it.errSchemaPath}/${keyword}`,
    topSchemaRef: schemaRef,
    compositeRule: true
  }, valid);
  cxt.pass(valid, () => cxt.error(true));
}
keyword.macroKeywordCode = macroKeywordCode;
function funcKeywordCode(cxt, def) {
  var _a;
  const {
    gen,
    keyword,
    schema,
    parentSchema,
    $data,
    it
  } = cxt;
  checkAsyncKeyword(it, def);
  const validate = !$data && def.compile ? def.compile.call(it.self, schema, parentSchema, it) : def.validate;
  const validateRef = useKeyword(gen, keyword, validate);
  const valid = gen.let("valid");
  cxt.block$data(valid, validateKeyword);
  cxt.ok((_a = def.valid) !== null && _a !== void 0 ? _a : valid);
  function validateKeyword() {
    if (def.errors === false) {
      assignValid();
      if (def.modifying) modifyData(cxt);
      reportErrs(() => cxt.error());
    } else {
      const ruleErrs = def.async ? validateAsync() : validateSync();
      if (def.modifying) modifyData(cxt);
      reportErrs(() => addErrs(cxt, ruleErrs));
    }
  }
  function validateAsync() {
    const ruleErrs = gen.let("ruleErrs", null);
    gen.try(() => assignValid((0, codegen_1$p._)`await `), e => gen.assign(valid, false).if((0, codegen_1$p._)`${e} instanceof ${it.ValidationError}`, () => gen.assign(ruleErrs, (0, codegen_1$p._)`${e}.errors`), () => gen.throw(e)));
    return ruleErrs;
  }
  function validateSync() {
    const validateErrs = (0, codegen_1$p._)`${validateRef}.errors`;
    gen.assign(validateErrs, null);
    assignValid(codegen_1$p.nil);
    return validateErrs;
  }
  function assignValid(_await = def.async ? (0, codegen_1$p._)`await ` : codegen_1$p.nil) {
    const passCxt = it.opts.passContext ? names_1$4.default.this : names_1$4.default.self;
    const passSchema = !("compile" in def && !$data || def.schema === false);
    gen.assign(valid, (0, codegen_1$p._)`${_await}${(0, code_1$9.callValidateCode)(cxt, validateRef, passCxt, passSchema)}`, def.modifying);
  }
  function reportErrs(errors) {
    var _a;
    gen.if((0, codegen_1$p.not)((_a = def.valid) !== null && _a !== void 0 ? _a : valid), errors);
  }
}
keyword.funcKeywordCode = funcKeywordCode;
function modifyData(cxt) {
  const {
    gen,
    data,
    it
  } = cxt;
  gen.if(it.parentData, () => gen.assign(data, (0, codegen_1$p._)`${it.parentData}[${it.parentDataProperty}]`));
}
function addErrs(cxt, errs) {
  const {
    gen
  } = cxt;
  gen.if((0, codegen_1$p._)`Array.isArray(${errs})`, () => {
    gen.assign(names_1$4.default.vErrors, (0, codegen_1$p._)`${names_1$4.default.vErrors} === null ? ${errs} : ${names_1$4.default.vErrors}.concat(${errs})`).assign(names_1$4.default.errors, (0, codegen_1$p._)`${names_1$4.default.vErrors}.length`);
    (0, errors_1$1.extendErrors)(cxt);
  }, () => cxt.error());
}
function checkAsyncKeyword({
  schemaEnv
}, def) {
  if (def.async && !schemaEnv.$async) throw new Error("async keyword in sync schema");
}
function useKeyword(gen, keyword, result) {
  if (result === undefined) throw new Error(`keyword "${keyword}" failed to compile`);
  return gen.scopeValue("keyword", typeof result == "function" ? {
    ref: result
  } : {
    ref: result,
    code: (0, codegen_1$p.stringify)(result)
  });
}
function validSchemaType(schema, schemaType, allowUndefined = false) {
  // TODO add tests
  return !schemaType.length || schemaType.some(st => st === "array" ? Array.isArray(schema) : st === "object" ? schema && typeof schema == "object" && !Array.isArray(schema) : typeof schema == st || allowUndefined && typeof schema == "undefined");
}
keyword.validSchemaType = validSchemaType;
function validateKeywordUsage({
  schema,
  opts,
  self,
  errSchemaPath
}, def, keyword) {
  /* istanbul ignore if */
  if (Array.isArray(def.keyword) ? !def.keyword.includes(keyword) : def.keyword !== keyword) {
    throw new Error("ajv implementation error");
  }
  const deps = def.dependencies;
  if (deps === null || deps === void 0 ? void 0 : deps.some(kwd => !Object.prototype.hasOwnProperty.call(schema, kwd))) {
    throw new Error(`parent schema must have dependencies of ${keyword}: ${deps.join(",")}`);
  }
  if (def.validateSchema) {
    const valid = def.validateSchema(schema[keyword]);
    if (!valid) {
      const msg = `keyword "${keyword}" value is invalid at path "${errSchemaPath}": ` + self.errorsText(def.validateSchema.errors);
      if (opts.validateSchema === "log") self.logger.error(msg);else throw new Error(msg);
    }
  }
}
keyword.validateKeywordUsage = validateKeywordUsage;

var subschema = {};

Object.defineProperty(subschema, "__esModule", {
  value: true
});
subschema.extendSubschemaMode = subschema.extendSubschemaData = subschema.getSubschema = void 0;
const codegen_1$o = codegen;
const util_1$n = util;
function getSubschema(it, {
  keyword,
  schemaProp,
  schema,
  schemaPath,
  errSchemaPath,
  topSchemaRef
}) {
  if (keyword !== undefined && schema !== undefined) {
    throw new Error('both "keyword" and "schema" passed, only one allowed');
  }
  if (keyword !== undefined) {
    const sch = it.schema[keyword];
    return schemaProp === undefined ? {
      schema: sch,
      schemaPath: (0, codegen_1$o._)`${it.schemaPath}${(0, codegen_1$o.getProperty)(keyword)}`,
      errSchemaPath: `${it.errSchemaPath}/${keyword}`
    } : {
      schema: sch[schemaProp],
      schemaPath: (0, codegen_1$o._)`${it.schemaPath}${(0, codegen_1$o.getProperty)(keyword)}${(0, codegen_1$o.getProperty)(schemaProp)}`,
      errSchemaPath: `${it.errSchemaPath}/${keyword}/${(0, util_1$n.escapeFragment)(schemaProp)}`
    };
  }
  if (schema !== undefined) {
    if (schemaPath === undefined || errSchemaPath === undefined || topSchemaRef === undefined) {
      throw new Error('"schemaPath", "errSchemaPath" and "topSchemaRef" are required with "schema"');
    }
    return {
      schema,
      schemaPath,
      topSchemaRef,
      errSchemaPath
    };
  }
  throw new Error('either "keyword" or "schema" must be passed');
}
subschema.getSubschema = getSubschema;
function extendSubschemaData(subschema, it, {
  dataProp,
  dataPropType: dpType,
  data,
  dataTypes,
  propertyName
}) {
  if (data !== undefined && dataProp !== undefined) {
    throw new Error('both "data" and "dataProp" passed, only one allowed');
  }
  const {
    gen
  } = it;
  if (dataProp !== undefined) {
    const {
      errorPath,
      dataPathArr,
      opts
    } = it;
    const nextData = gen.let("data", (0, codegen_1$o._)`${it.data}${(0, codegen_1$o.getProperty)(dataProp)}`, true);
    dataContextProps(nextData);
    subschema.errorPath = (0, codegen_1$o.str)`${errorPath}${(0, util_1$n.getErrorPath)(dataProp, dpType, opts.jsPropertySyntax)}`;
    subschema.parentDataProperty = (0, codegen_1$o._)`${dataProp}`;
    subschema.dataPathArr = [...dataPathArr, subschema.parentDataProperty];
  }
  if (data !== undefined) {
    const nextData = data instanceof codegen_1$o.Name ? data : gen.let("data", data, true); // replaceable if used once?
    dataContextProps(nextData);
    if (propertyName !== undefined) subschema.propertyName = propertyName;
    // TODO something is possibly wrong here with not changing parentDataProperty and not appending dataPathArr
  }
  if (dataTypes) subschema.dataTypes = dataTypes;
  function dataContextProps(_nextData) {
    subschema.data = _nextData;
    subschema.dataLevel = it.dataLevel + 1;
    subschema.dataTypes = [];
    it.definedProperties = new Set();
    subschema.parentData = it.data;
    subschema.dataNames = [...it.dataNames, _nextData];
  }
}
subschema.extendSubschemaData = extendSubschemaData;
function extendSubschemaMode(subschema, {
  jtdDiscriminator,
  jtdMetadata,
  compositeRule,
  createErrors,
  allErrors
}) {
  if (compositeRule !== undefined) subschema.compositeRule = compositeRule;
  if (createErrors !== undefined) subschema.createErrors = createErrors;
  if (allErrors !== undefined) subschema.allErrors = allErrors;
  subschema.jtdDiscriminator = jtdDiscriminator; // not inherited
  subschema.jtdMetadata = jtdMetadata; // not inherited
}
subschema.extendSubschemaMode = extendSubschemaMode;

var resolve$2 = {};

// do not edit .js files directly - edit src/index.jst
var fastDeepEqual = function equal(a, b) {
  if (a === b) return true;
  if (a && b && typeof a == 'object' && typeof b == 'object') {
    if (a.constructor !== b.constructor) return false;
    var length, i, keys;
    if (Array.isArray(a)) {
      length = a.length;
      if (length != b.length) return false;
      for (i = length; i-- !== 0;) if (!equal(a[i], b[i])) return false;
      return true;
    }
    if (a.constructor === RegExp) return a.source === b.source && a.flags === b.flags;
    if (a.valueOf !== Object.prototype.valueOf) return a.valueOf() === b.valueOf();
    if (a.toString !== Object.prototype.toString) return a.toString() === b.toString();
    keys = Object.keys(a);
    length = keys.length;
    if (length !== Object.keys(b).length) return false;
    for (i = length; i-- !== 0;) if (!Object.prototype.hasOwnProperty.call(b, keys[i])) return false;
    for (i = length; i-- !== 0;) {
      var key = keys[i];
      if (!equal(a[key], b[key])) return false;
    }
    return true;
  }

  // true if both NaN, false otherwise
  return a !== a && b !== b;
};

var jsonSchemaTraverse = {exports: {}};

var traverse$1 = jsonSchemaTraverse.exports = function (schema, opts, cb) {
  // Legacy support for v0.3.1 and earlier.
  if (typeof opts == 'function') {
    cb = opts;
    opts = {};
  }
  cb = opts.cb || cb;
  var pre = typeof cb == 'function' ? cb : cb.pre || function () {};
  var post = cb.post || function () {};
  _traverse(opts, pre, post, schema, '', schema);
};
traverse$1.keywords = {
  additionalItems: true,
  items: true,
  contains: true,
  additionalProperties: true,
  propertyNames: true,
  not: true,
  if: true,
  then: true,
  else: true
};
traverse$1.arrayKeywords = {
  items: true,
  allOf: true,
  anyOf: true,
  oneOf: true
};
traverse$1.propsKeywords = {
  $defs: true,
  definitions: true,
  properties: true,
  patternProperties: true,
  dependencies: true
};
traverse$1.skipKeywords = {
  default: true,
  enum: true,
  const: true,
  required: true,
  maximum: true,
  minimum: true,
  exclusiveMaximum: true,
  exclusiveMinimum: true,
  multipleOf: true,
  maxLength: true,
  minLength: true,
  pattern: true,
  format: true,
  maxItems: true,
  minItems: true,
  uniqueItems: true,
  maxProperties: true,
  minProperties: true
};
function _traverse(opts, pre, post, schema, jsonPtr, rootSchema, parentJsonPtr, parentKeyword, parentSchema, keyIndex) {
  if (schema && typeof schema == 'object' && !Array.isArray(schema)) {
    pre(schema, jsonPtr, rootSchema, parentJsonPtr, parentKeyword, parentSchema, keyIndex);
    for (var key in schema) {
      var sch = schema[key];
      if (Array.isArray(sch)) {
        if (key in traverse$1.arrayKeywords) {
          for (var i = 0; i < sch.length; i++) _traverse(opts, pre, post, sch[i], jsonPtr + '/' + key + '/' + i, rootSchema, jsonPtr, key, schema, i);
        }
      } else if (key in traverse$1.propsKeywords) {
        if (sch && typeof sch == 'object') {
          for (var prop in sch) _traverse(opts, pre, post, sch[prop], jsonPtr + '/' + key + '/' + escapeJsonPtr(prop), rootSchema, jsonPtr, key, schema, prop);
        }
      } else if (key in traverse$1.keywords || opts.allKeys && !(key in traverse$1.skipKeywords)) {
        _traverse(opts, pre, post, sch, jsonPtr + '/' + key, rootSchema, jsonPtr, key, schema);
      }
    }
    post(schema, jsonPtr, rootSchema, parentJsonPtr, parentKeyword, parentSchema, keyIndex);
  }
}
function escapeJsonPtr(str) {
  return str.replace(/~/g, '~0').replace(/\//g, '~1');
}

var jsonSchemaTraverseExports = jsonSchemaTraverse.exports;

Object.defineProperty(resolve$2, "__esModule", {
  value: true
});
resolve$2.getSchemaRefs = resolve$2.resolveUrl = resolve$2.normalizeId = resolve$2._getFullPath = resolve$2.getFullPath = resolve$2.inlineRef = void 0;
const util_1$m = util;
const equal$3 = fastDeepEqual;
const traverse = jsonSchemaTraverseExports;
// TODO refactor to use keyword definitions
const SIMPLE_INLINED = new Set(["type", "format", "pattern", "maxLength", "minLength", "maxProperties", "minProperties", "maxItems", "minItems", "maximum", "minimum", "uniqueItems", "multipleOf", "required", "enum", "const"]);
function inlineRef(schema, limit = true) {
  if (typeof schema == "boolean") return true;
  if (limit === true) return !hasRef(schema);
  if (!limit) return false;
  return countKeys(schema) <= limit;
}
resolve$2.inlineRef = inlineRef;
const REF_KEYWORDS = new Set(["$ref", "$recursiveRef", "$recursiveAnchor", "$dynamicRef", "$dynamicAnchor"]);
function hasRef(schema) {
  for (const key in schema) {
    if (REF_KEYWORDS.has(key)) return true;
    const sch = schema[key];
    if (Array.isArray(sch) && sch.some(hasRef)) return true;
    if (typeof sch == "object" && hasRef(sch)) return true;
  }
  return false;
}
function countKeys(schema) {
  let count = 0;
  for (const key in schema) {
    if (key === "$ref") return Infinity;
    count++;
    if (SIMPLE_INLINED.has(key)) continue;
    if (typeof schema[key] == "object") {
      (0, util_1$m.eachItem)(schema[key], sch => count += countKeys(sch));
    }
    if (count === Infinity) return Infinity;
  }
  return count;
}
function getFullPath(resolver, id = "", normalize) {
  if (normalize !== false) id = normalizeId(id);
  const p = resolver.parse(id);
  return _getFullPath(resolver, p);
}
resolve$2.getFullPath = getFullPath;
function _getFullPath(resolver, p) {
  const serialized = resolver.serialize(p);
  return serialized.split("#")[0] + "#";
}
resolve$2._getFullPath = _getFullPath;
const TRAILING_SLASH_HASH = /#\/?$/;
function normalizeId(id) {
  return id ? id.replace(TRAILING_SLASH_HASH, "") : "";
}
resolve$2.normalizeId = normalizeId;
function resolveUrl(resolver, baseId, id) {
  id = normalizeId(id);
  return resolver.resolve(baseId, id);
}
resolve$2.resolveUrl = resolveUrl;
const ANCHOR = /^[a-z_][-a-z0-9._]*$/i;
function getSchemaRefs(schema, baseId) {
  if (typeof schema == "boolean") return {};
  const {
    schemaId,
    uriResolver
  } = this.opts;
  const schId = normalizeId(schema[schemaId] || baseId);
  const baseIds = {
    "": schId
  };
  const pathPrefix = getFullPath(uriResolver, schId, false);
  const localRefs = {};
  const schemaRefs = new Set();
  traverse(schema, {
    allKeys: true
  }, (sch, jsonPtr, _, parentJsonPtr) => {
    if (parentJsonPtr === undefined) return;
    const fullPath = pathPrefix + jsonPtr;
    let innerBaseId = baseIds[parentJsonPtr];
    if (typeof sch[schemaId] == "string") innerBaseId = addRef.call(this, sch[schemaId]);
    addAnchor.call(this, sch.$anchor);
    addAnchor.call(this, sch.$dynamicAnchor);
    baseIds[jsonPtr] = innerBaseId;
    function addRef(ref) {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      const _resolve = this.opts.uriResolver.resolve;
      ref = normalizeId(innerBaseId ? _resolve(innerBaseId, ref) : ref);
      if (schemaRefs.has(ref)) throw ambiguos(ref);
      schemaRefs.add(ref);
      let schOrRef = this.refs[ref];
      if (typeof schOrRef == "string") schOrRef = this.refs[schOrRef];
      if (typeof schOrRef == "object") {
        checkAmbiguosRef(sch, schOrRef.schema, ref);
      } else if (ref !== normalizeId(fullPath)) {
        if (ref[0] === "#") {
          checkAmbiguosRef(sch, localRefs[ref], ref);
          localRefs[ref] = sch;
        } else {
          this.refs[ref] = fullPath;
        }
      }
      return ref;
    }
    function addAnchor(anchor) {
      if (typeof anchor == "string") {
        if (!ANCHOR.test(anchor)) throw new Error(`invalid anchor "${anchor}"`);
        addRef.call(this, `#${anchor}`);
      }
    }
  });
  return localRefs;
  function checkAmbiguosRef(sch1, sch2, ref) {
    if (sch2 !== undefined && !equal$3(sch1, sch2)) throw ambiguos(ref);
  }
  function ambiguos(ref) {
    return new Error(`reference "${ref}" resolves to more than one schema`);
  }
}
resolve$2.getSchemaRefs = getSchemaRefs;

Object.defineProperty(validate, "__esModule", {
  value: true
});
validate.getData = validate.KeywordCxt = validate.validateFunctionCode = void 0;
const boolSchema_1 = boolSchema;
const dataType_1$1 = dataType;
const applicability_1 = applicability;
const dataType_2 = dataType;
const defaults_1 = defaults;
const keyword_1 = keyword;
const subschema_1 = subschema;
const codegen_1$n = codegen;
const names_1$3 = names$1;
const resolve_1$2 = resolve$2;
const util_1$l = util;
const errors_1 = errors;
// schema compilation - generates validation function, subschemaCode (below) is used for subschemas
function validateFunctionCode(it) {
  if (isSchemaObj(it)) {
    checkKeywords(it);
    if (schemaCxtHasRules(it)) {
      topSchemaObjCode(it);
      return;
    }
  }
  validateFunction(it, () => (0, boolSchema_1.topBoolOrEmptySchema)(it));
}
validate.validateFunctionCode = validateFunctionCode;
function validateFunction({
  gen,
  validateName,
  schema,
  schemaEnv,
  opts
}, body) {
  if (opts.code.es5) {
    gen.func(validateName, (0, codegen_1$n._)`${names_1$3.default.data}, ${names_1$3.default.valCxt}`, schemaEnv.$async, () => {
      gen.code((0, codegen_1$n._)`"use strict"; ${funcSourceUrl(schema, opts)}`);
      destructureValCxtES5(gen, opts);
      gen.code(body);
    });
  } else {
    gen.func(validateName, (0, codegen_1$n._)`${names_1$3.default.data}, ${destructureValCxt(opts)}`, schemaEnv.$async, () => gen.code(funcSourceUrl(schema, opts)).code(body));
  }
}
function destructureValCxt(opts) {
  return (0, codegen_1$n._)`{${names_1$3.default.instancePath}="", ${names_1$3.default.parentData}, ${names_1$3.default.parentDataProperty}, ${names_1$3.default.rootData}=${names_1$3.default.data}${opts.dynamicRef ? (0, codegen_1$n._)`, ${names_1$3.default.dynamicAnchors}={}` : codegen_1$n.nil}}={}`;
}
function destructureValCxtES5(gen, opts) {
  gen.if(names_1$3.default.valCxt, () => {
    gen.var(names_1$3.default.instancePath, (0, codegen_1$n._)`${names_1$3.default.valCxt}.${names_1$3.default.instancePath}`);
    gen.var(names_1$3.default.parentData, (0, codegen_1$n._)`${names_1$3.default.valCxt}.${names_1$3.default.parentData}`);
    gen.var(names_1$3.default.parentDataProperty, (0, codegen_1$n._)`${names_1$3.default.valCxt}.${names_1$3.default.parentDataProperty}`);
    gen.var(names_1$3.default.rootData, (0, codegen_1$n._)`${names_1$3.default.valCxt}.${names_1$3.default.rootData}`);
    if (opts.dynamicRef) gen.var(names_1$3.default.dynamicAnchors, (0, codegen_1$n._)`${names_1$3.default.valCxt}.${names_1$3.default.dynamicAnchors}`);
  }, () => {
    gen.var(names_1$3.default.instancePath, (0, codegen_1$n._)`""`);
    gen.var(names_1$3.default.parentData, (0, codegen_1$n._)`undefined`);
    gen.var(names_1$3.default.parentDataProperty, (0, codegen_1$n._)`undefined`);
    gen.var(names_1$3.default.rootData, names_1$3.default.data);
    if (opts.dynamicRef) gen.var(names_1$3.default.dynamicAnchors, (0, codegen_1$n._)`{}`);
  });
}
function topSchemaObjCode(it) {
  const {
    schema,
    opts,
    gen
  } = it;
  validateFunction(it, () => {
    if (opts.$comment && schema.$comment) commentKeyword(it);
    checkNoDefault(it);
    gen.let(names_1$3.default.vErrors, null);
    gen.let(names_1$3.default.errors, 0);
    if (opts.unevaluated) resetEvaluated(it);
    typeAndKeywords(it);
    returnResults(it);
  });
  return;
}
function resetEvaluated(it) {
  // TODO maybe some hook to execute it in the end to check whether props/items are Name, as in assignEvaluated
  const {
    gen,
    validateName
  } = it;
  it.evaluated = gen.const("evaluated", (0, codegen_1$n._)`${validateName}.evaluated`);
  gen.if((0, codegen_1$n._)`${it.evaluated}.dynamicProps`, () => gen.assign((0, codegen_1$n._)`${it.evaluated}.props`, (0, codegen_1$n._)`undefined`));
  gen.if((0, codegen_1$n._)`${it.evaluated}.dynamicItems`, () => gen.assign((0, codegen_1$n._)`${it.evaluated}.items`, (0, codegen_1$n._)`undefined`));
}
function funcSourceUrl(schema, opts) {
  const schId = typeof schema == "object" && schema[opts.schemaId];
  return schId && (opts.code.source || opts.code.process) ? (0, codegen_1$n._)`/*# sourceURL=${schId} */` : codegen_1$n.nil;
}
// schema compilation - this function is used recursively to generate code for sub-schemas
function subschemaCode(it, valid) {
  if (isSchemaObj(it)) {
    checkKeywords(it);
    if (schemaCxtHasRules(it)) {
      subSchemaObjCode(it, valid);
      return;
    }
  }
  (0, boolSchema_1.boolOrEmptySchema)(it, valid);
}
function schemaCxtHasRules({
  schema,
  self
}) {
  if (typeof schema == "boolean") return !schema;
  for (const key in schema) if (self.RULES.all[key]) return true;
  return false;
}
function isSchemaObj(it) {
  return typeof it.schema != "boolean";
}
function subSchemaObjCode(it, valid) {
  const {
    schema,
    gen,
    opts
  } = it;
  if (opts.$comment && schema.$comment) commentKeyword(it);
  updateContext(it);
  checkAsyncSchema(it);
  const errsCount = gen.const("_errs", names_1$3.default.errors);
  typeAndKeywords(it, errsCount);
  // TODO var
  gen.var(valid, (0, codegen_1$n._)`${errsCount} === ${names_1$3.default.errors}`);
}
function checkKeywords(it) {
  (0, util_1$l.checkUnknownRules)(it);
  checkRefsAndKeywords(it);
}
function typeAndKeywords(it, errsCount) {
  if (it.opts.jtd) return schemaKeywords(it, [], false, errsCount);
  const types = (0, dataType_1$1.getSchemaTypes)(it.schema);
  const checkedTypes = (0, dataType_1$1.coerceAndCheckDataType)(it, types);
  schemaKeywords(it, types, !checkedTypes, errsCount);
}
function checkRefsAndKeywords(it) {
  const {
    schema,
    errSchemaPath,
    opts,
    self
  } = it;
  if (schema.$ref && opts.ignoreKeywordsWithRef && (0, util_1$l.schemaHasRulesButRef)(schema, self.RULES)) {
    self.logger.warn(`$ref: keywords ignored in schema at path "${errSchemaPath}"`);
  }
}
function checkNoDefault(it) {
  const {
    schema,
    opts
  } = it;
  if (schema.default !== undefined && opts.useDefaults && opts.strictSchema) {
    (0, util_1$l.checkStrictMode)(it, "default is ignored in the schema root");
  }
}
function updateContext(it) {
  const schId = it.schema[it.opts.schemaId];
  if (schId) it.baseId = (0, resolve_1$2.resolveUrl)(it.opts.uriResolver, it.baseId, schId);
}
function checkAsyncSchema(it) {
  if (it.schema.$async && !it.schemaEnv.$async) throw new Error("async schema in sync schema");
}
function commentKeyword({
  gen,
  schemaEnv,
  schema,
  errSchemaPath,
  opts
}) {
  const msg = schema.$comment;
  if (opts.$comment === true) {
    gen.code((0, codegen_1$n._)`${names_1$3.default.self}.logger.log(${msg})`);
  } else if (typeof opts.$comment == "function") {
    const schemaPath = (0, codegen_1$n.str)`${errSchemaPath}/$comment`;
    const rootName = gen.scopeValue("root", {
      ref: schemaEnv.root
    });
    gen.code((0, codegen_1$n._)`${names_1$3.default.self}.opts.$comment(${msg}, ${schemaPath}, ${rootName}.schema)`);
  }
}
function returnResults(it) {
  const {
    gen,
    schemaEnv,
    validateName,
    ValidationError,
    opts
  } = it;
  if (schemaEnv.$async) {
    // TODO assign unevaluated
    gen.if((0, codegen_1$n._)`${names_1$3.default.errors} === 0`, () => gen.return(names_1$3.default.data), () => gen.throw((0, codegen_1$n._)`new ${ValidationError}(${names_1$3.default.vErrors})`));
  } else {
    gen.assign((0, codegen_1$n._)`${validateName}.errors`, names_1$3.default.vErrors);
    if (opts.unevaluated) assignEvaluated(it);
    gen.return((0, codegen_1$n._)`${names_1$3.default.errors} === 0`);
  }
}
function assignEvaluated({
  gen,
  evaluated,
  props,
  items
}) {
  if (props instanceof codegen_1$n.Name) gen.assign((0, codegen_1$n._)`${evaluated}.props`, props);
  if (items instanceof codegen_1$n.Name) gen.assign((0, codegen_1$n._)`${evaluated}.items`, items);
}
function schemaKeywords(it, types, typeErrors, errsCount) {
  const {
    gen,
    schema,
    data,
    allErrors,
    opts,
    self
  } = it;
  const {
    RULES
  } = self;
  if (schema.$ref && (opts.ignoreKeywordsWithRef || !(0, util_1$l.schemaHasRulesButRef)(schema, RULES))) {
    gen.block(() => keywordCode(it, "$ref", RULES.all.$ref.definition)); // TODO typecast
    return;
  }
  if (!opts.jtd) checkStrictTypes(it, types);
  gen.block(() => {
    for (const group of RULES.rules) groupKeywords(group);
    groupKeywords(RULES.post);
  });
  function groupKeywords(group) {
    if (!(0, applicability_1.shouldUseGroup)(schema, group)) return;
    if (group.type) {
      gen.if((0, dataType_2.checkDataType)(group.type, data, opts.strictNumbers));
      iterateKeywords(it, group);
      if (types.length === 1 && types[0] === group.type && typeErrors) {
        gen.else();
        (0, dataType_2.reportTypeError)(it);
      }
      gen.endIf();
    } else {
      iterateKeywords(it, group);
    }
    // TODO make it "ok" call?
    if (!allErrors) gen.if((0, codegen_1$n._)`${names_1$3.default.errors} === ${errsCount || 0}`);
  }
}
function iterateKeywords(it, group) {
  const {
    gen,
    schema,
    opts: {
      useDefaults
    }
  } = it;
  if (useDefaults) (0, defaults_1.assignDefaults)(it, group.type);
  gen.block(() => {
    for (const rule of group.rules) {
      if ((0, applicability_1.shouldUseRule)(schema, rule)) {
        keywordCode(it, rule.keyword, rule.definition, group.type);
      }
    }
  });
}
function checkStrictTypes(it, types) {
  if (it.schemaEnv.meta || !it.opts.strictTypes) return;
  checkContextTypes(it, types);
  if (!it.opts.allowUnionTypes) checkMultipleTypes(it, types);
  checkKeywordTypes(it, it.dataTypes);
}
function checkContextTypes(it, types) {
  if (!types.length) return;
  if (!it.dataTypes.length) {
    it.dataTypes = types;
    return;
  }
  types.forEach(t => {
    if (!includesType(it.dataTypes, t)) {
      strictTypesError(it, `type "${t}" not allowed by context "${it.dataTypes.join(",")}"`);
    }
  });
  narrowSchemaTypes(it, types);
}
function checkMultipleTypes(it, ts) {
  if (ts.length > 1 && !(ts.length === 2 && ts.includes("null"))) {
    strictTypesError(it, "use allowUnionTypes to allow union type keyword");
  }
}
function checkKeywordTypes(it, ts) {
  const rules = it.self.RULES.all;
  for (const keyword in rules) {
    const rule = rules[keyword];
    if (typeof rule == "object" && (0, applicability_1.shouldUseRule)(it.schema, rule)) {
      const {
        type
      } = rule.definition;
      if (type.length && !type.some(t => hasApplicableType(ts, t))) {
        strictTypesError(it, `missing type "${type.join(",")}" for keyword "${keyword}"`);
      }
    }
  }
}
function hasApplicableType(schTs, kwdT) {
  return schTs.includes(kwdT) || kwdT === "number" && schTs.includes("integer");
}
function includesType(ts, t) {
  return ts.includes(t) || t === "integer" && ts.includes("number");
}
function narrowSchemaTypes(it, withTypes) {
  const ts = [];
  for (const t of it.dataTypes) {
    if (includesType(withTypes, t)) ts.push(t);else if (withTypes.includes("integer") && t === "number") ts.push("integer");
  }
  it.dataTypes = ts;
}
function strictTypesError(it, msg) {
  const schemaPath = it.schemaEnv.baseId + it.errSchemaPath;
  msg += ` at "${schemaPath}" (strictTypes)`;
  (0, util_1$l.checkStrictMode)(it, msg, it.opts.strictTypes);
}
class KeywordCxt {
  constructor(it, def, keyword) {
    (0, keyword_1.validateKeywordUsage)(it, def, keyword);
    this.gen = it.gen;
    this.allErrors = it.allErrors;
    this.keyword = keyword;
    this.data = it.data;
    this.schema = it.schema[keyword];
    this.$data = def.$data && it.opts.$data && this.schema && this.schema.$data;
    this.schemaValue = (0, util_1$l.schemaRefOrVal)(it, this.schema, keyword, this.$data);
    this.schemaType = def.schemaType;
    this.parentSchema = it.schema;
    this.params = {};
    this.it = it;
    this.def = def;
    if (this.$data) {
      this.schemaCode = it.gen.const("vSchema", getData(this.$data, it));
    } else {
      this.schemaCode = this.schemaValue;
      if (!(0, keyword_1.validSchemaType)(this.schema, def.schemaType, def.allowUndefined)) {
        throw new Error(`${keyword} value must be ${JSON.stringify(def.schemaType)}`);
      }
    }
    if ("code" in def ? def.trackErrors : def.errors !== false) {
      this.errsCount = it.gen.const("_errs", names_1$3.default.errors);
    }
  }
  result(condition, successAction, failAction) {
    this.failResult((0, codegen_1$n.not)(condition), successAction, failAction);
  }
  failResult(condition, successAction, failAction) {
    this.gen.if(condition);
    if (failAction) failAction();else this.error();
    if (successAction) {
      this.gen.else();
      successAction();
      if (this.allErrors) this.gen.endIf();
    } else {
      if (this.allErrors) this.gen.endIf();else this.gen.else();
    }
  }
  pass(condition, failAction) {
    this.failResult((0, codegen_1$n.not)(condition), undefined, failAction);
  }
  fail(condition) {
    if (condition === undefined) {
      this.error();
      if (!this.allErrors) this.gen.if(false); // this branch will be removed by gen.optimize
      return;
    }
    this.gen.if(condition);
    this.error();
    if (this.allErrors) this.gen.endIf();else this.gen.else();
  }
  fail$data(condition) {
    if (!this.$data) return this.fail(condition);
    const {
      schemaCode
    } = this;
    this.fail((0, codegen_1$n._)`${schemaCode} !== undefined && (${(0, codegen_1$n.or)(this.invalid$data(), condition)})`);
  }
  error(append, errorParams, errorPaths) {
    if (errorParams) {
      this.setParams(errorParams);
      this._error(append, errorPaths);
      this.setParams({});
      return;
    }
    this._error(append, errorPaths);
  }
  _error(append, errorPaths) {
    (append ? errors_1.reportExtraError : errors_1.reportError)(this, this.def.error, errorPaths);
  }
  $dataError() {
    (0, errors_1.reportError)(this, this.def.$dataError || errors_1.keyword$DataError);
  }
  reset() {
    if (this.errsCount === undefined) throw new Error('add "trackErrors" to keyword definition');
    (0, errors_1.resetErrorsCount)(this.gen, this.errsCount);
  }
  ok(cond) {
    if (!this.allErrors) this.gen.if(cond);
  }
  setParams(obj, assign) {
    if (assign) Object.assign(this.params, obj);else this.params = obj;
  }
  block$data(valid, codeBlock, $dataValid = codegen_1$n.nil) {
    this.gen.block(() => {
      this.check$data(valid, $dataValid);
      codeBlock();
    });
  }
  check$data(valid = codegen_1$n.nil, $dataValid = codegen_1$n.nil) {
    if (!this.$data) return;
    const {
      gen,
      schemaCode,
      schemaType,
      def
    } = this;
    gen.if((0, codegen_1$n.or)((0, codegen_1$n._)`${schemaCode} === undefined`, $dataValid));
    if (valid !== codegen_1$n.nil) gen.assign(valid, true);
    if (schemaType.length || def.validateSchema) {
      gen.elseIf(this.invalid$data());
      this.$dataError();
      if (valid !== codegen_1$n.nil) gen.assign(valid, false);
    }
    gen.else();
  }
  invalid$data() {
    const {
      gen,
      schemaCode,
      schemaType,
      def,
      it
    } = this;
    return (0, codegen_1$n.or)(wrong$DataType(), invalid$DataSchema());
    function wrong$DataType() {
      if (schemaType.length) {
        /* istanbul ignore if */
        if (!(schemaCode instanceof codegen_1$n.Name)) throw new Error("ajv implementation error");
        const st = Array.isArray(schemaType) ? schemaType : [schemaType];
        return (0, codegen_1$n._)`${(0, dataType_2.checkDataTypes)(st, schemaCode, it.opts.strictNumbers, dataType_2.DataType.Wrong)}`;
      }
      return codegen_1$n.nil;
    }
    function invalid$DataSchema() {
      if (def.validateSchema) {
        const validateSchemaRef = gen.scopeValue("validate$data", {
          ref: def.validateSchema
        }); // TODO value.code for standalone
        return (0, codegen_1$n._)`!${validateSchemaRef}(${schemaCode})`;
      }
      return codegen_1$n.nil;
    }
  }
  subschema(appl, valid) {
    const subschema = (0, subschema_1.getSubschema)(this.it, appl);
    (0, subschema_1.extendSubschemaData)(subschema, this.it, appl);
    (0, subschema_1.extendSubschemaMode)(subschema, appl);
    const nextContext = {
      ...this.it,
      ...subschema,
      items: undefined,
      props: undefined
    };
    subschemaCode(nextContext, valid);
    return nextContext;
  }
  mergeEvaluated(schemaCxt, toName) {
    const {
      it,
      gen
    } = this;
    if (!it.opts.unevaluated) return;
    if (it.props !== true && schemaCxt.props !== undefined) {
      it.props = util_1$l.mergeEvaluated.props(gen, schemaCxt.props, it.props, toName);
    }
    if (it.items !== true && schemaCxt.items !== undefined) {
      it.items = util_1$l.mergeEvaluated.items(gen, schemaCxt.items, it.items, toName);
    }
  }
  mergeValidEvaluated(schemaCxt, valid) {
    const {
      it,
      gen
    } = this;
    if (it.opts.unevaluated && (it.props !== true || it.items !== true)) {
      gen.if(valid, () => this.mergeEvaluated(schemaCxt, codegen_1$n.Name));
      return true;
    }
  }
}
validate.KeywordCxt = KeywordCxt;
function keywordCode(it, keyword, def, ruleType) {
  const cxt = new KeywordCxt(it, def, keyword);
  if ("code" in def) {
    def.code(cxt, ruleType);
  } else if (cxt.$data && def.validate) {
    (0, keyword_1.funcKeywordCode)(cxt, def);
  } else if ("macro" in def) {
    (0, keyword_1.macroKeywordCode)(cxt, def);
  } else if (def.compile || def.validate) {
    (0, keyword_1.funcKeywordCode)(cxt, def);
  }
}
const JSON_POINTER = /^\/(?:[^~]|~0|~1)*$/;
const RELATIVE_JSON_POINTER = /^([0-9]+)(#|\/(?:[^~]|~0|~1)*)?$/;
function getData($data, {
  dataLevel,
  dataNames,
  dataPathArr
}) {
  let jsonPointer;
  let data;
  if ($data === "") return names_1$3.default.rootData;
  if ($data[0] === "/") {
    if (!JSON_POINTER.test($data)) throw new Error(`Invalid JSON-pointer: ${$data}`);
    jsonPointer = $data;
    data = names_1$3.default.rootData;
  } else {
    const matches = RELATIVE_JSON_POINTER.exec($data);
    if (!matches) throw new Error(`Invalid JSON-pointer: ${$data}`);
    const up = +matches[1];
    jsonPointer = matches[2];
    if (jsonPointer === "#") {
      if (up >= dataLevel) throw new Error(errorMsg("property/index", up));
      return dataPathArr[dataLevel - up];
    }
    if (up > dataLevel) throw new Error(errorMsg("data", up));
    data = dataNames[dataLevel - up];
    if (!jsonPointer) return data;
  }
  let expr = data;
  const segments = jsonPointer.split("/");
  for (const segment of segments) {
    if (segment) {
      data = (0, codegen_1$n._)`${data}${(0, codegen_1$n.getProperty)((0, util_1$l.unescapeJsonPointer)(segment))}`;
      expr = (0, codegen_1$n._)`${expr} && ${data}`;
    }
  }
  return expr;
  function errorMsg(pointerType, up) {
    return `Cannot access ${pointerType} ${up} levels up, current level is ${dataLevel}`;
  }
}
validate.getData = getData;

var validation_error = {};

Object.defineProperty(validation_error, "__esModule", {
  value: true
});
class ValidationError extends Error {
  constructor(errors) {
    super("validation failed");
    this.errors = errors;
    this.ajv = this.validation = true;
  }
}
validation_error.default = ValidationError;

var ref_error = {};

Object.defineProperty(ref_error, "__esModule", {
  value: true
});
const resolve_1$1 = resolve$2;
class MissingRefError extends Error {
  constructor(resolver, baseId, ref, msg) {
    super(msg || `can't resolve reference ${ref} from id ${baseId}`);
    this.missingRef = (0, resolve_1$1.resolveUrl)(resolver, baseId, ref);
    this.missingSchema = (0, resolve_1$1.normalizeId)((0, resolve_1$1.getFullPath)(resolver, this.missingRef));
  }
}
ref_error.default = MissingRefError;

var compile = {};

Object.defineProperty(compile, "__esModule", {
  value: true
});
compile.resolveSchema = compile.getCompilingSchema = compile.resolveRef = compile.compileSchema = compile.SchemaEnv = void 0;
const codegen_1$m = codegen;
const validation_error_1 = validation_error;
const names_1$2 = names$1;
const resolve_1 = resolve$2;
const util_1$k = util;
const validate_1$1 = validate;
class SchemaEnv {
  constructor(env) {
    var _a;
    this.refs = {};
    this.dynamicAnchors = {};
    let schema;
    if (typeof env.schema == "object") schema = env.schema;
    this.schema = env.schema;
    this.schemaId = env.schemaId;
    this.root = env.root || this;
    this.baseId = (_a = env.baseId) !== null && _a !== void 0 ? _a : (0, resolve_1.normalizeId)(schema === null || schema === void 0 ? void 0 : schema[env.schemaId || "$id"]);
    this.schemaPath = env.schemaPath;
    this.localRefs = env.localRefs;
    this.meta = env.meta;
    this.$async = schema === null || schema === void 0 ? void 0 : schema.$async;
    this.refs = {};
  }
}
compile.SchemaEnv = SchemaEnv;
// let codeSize = 0
// let nodeCount = 0
// Compiles schema in SchemaEnv
function compileSchema(sch) {
  // TODO refactor - remove compilations
  const _sch = getCompilingSchema.call(this, sch);
  if (_sch) return _sch;
  const rootId = (0, resolve_1.getFullPath)(this.opts.uriResolver, sch.root.baseId); // TODO if getFullPath removed 1 tests fails
  const {
    es5,
    lines
  } = this.opts.code;
  const {
    ownProperties
  } = this.opts;
  const gen = new codegen_1$m.CodeGen(this.scope, {
    es5,
    lines,
    ownProperties
  });
  let _ValidationError;
  if (sch.$async) {
    _ValidationError = gen.scopeValue("Error", {
      ref: validation_error_1.default,
      code: (0, codegen_1$m._)`require("ajv/dist/runtime/validation_error").default`
    });
  }
  const validateName = gen.scopeName("validate");
  sch.validateName = validateName;
  const schemaCxt = {
    gen,
    allErrors: this.opts.allErrors,
    data: names_1$2.default.data,
    parentData: names_1$2.default.parentData,
    parentDataProperty: names_1$2.default.parentDataProperty,
    dataNames: [names_1$2.default.data],
    dataPathArr: [codegen_1$m.nil],
    // TODO can its length be used as dataLevel if nil is removed?
    dataLevel: 0,
    dataTypes: [],
    definedProperties: new Set(),
    topSchemaRef: gen.scopeValue("schema", this.opts.code.source === true ? {
      ref: sch.schema,
      code: (0, codegen_1$m.stringify)(sch.schema)
    } : {
      ref: sch.schema
    }),
    validateName,
    ValidationError: _ValidationError,
    schema: sch.schema,
    schemaEnv: sch,
    rootId,
    baseId: sch.baseId || rootId,
    schemaPath: codegen_1$m.nil,
    errSchemaPath: sch.schemaPath || (this.opts.jtd ? "" : "#"),
    errorPath: (0, codegen_1$m._)`""`,
    opts: this.opts,
    self: this
  };
  let sourceCode;
  try {
    this._compilations.add(sch);
    (0, validate_1$1.validateFunctionCode)(schemaCxt);
    gen.optimize(this.opts.code.optimize);
    // gen.optimize(1)
    const validateCode = gen.toString();
    sourceCode = `${gen.scopeRefs(names_1$2.default.scope)}return ${validateCode}`;
    // console.log((codeSize += sourceCode.length), (nodeCount += gen.nodeCount))
    if (this.opts.code.process) sourceCode = this.opts.code.process(sourceCode, sch);
    // console.log("\n\n\n *** \n", sourceCode)
    const makeValidate = new Function(`${names_1$2.default.self}`, `${names_1$2.default.scope}`, sourceCode);
    const validate = makeValidate(this, this.scope.get());
    this.scope.value(validateName, {
      ref: validate
    });
    validate.errors = null;
    validate.schema = sch.schema;
    validate.schemaEnv = sch;
    if (sch.$async) validate.$async = true;
    if (this.opts.code.source === true) {
      validate.source = {
        validateName,
        validateCode,
        scopeValues: gen._values
      };
    }
    if (this.opts.unevaluated) {
      const {
        props,
        items
      } = schemaCxt;
      validate.evaluated = {
        props: props instanceof codegen_1$m.Name ? undefined : props,
        items: items instanceof codegen_1$m.Name ? undefined : items,
        dynamicProps: props instanceof codegen_1$m.Name,
        dynamicItems: items instanceof codegen_1$m.Name
      };
      if (validate.source) validate.source.evaluated = (0, codegen_1$m.stringify)(validate.evaluated);
    }
    sch.validate = validate;
    return sch;
  } catch (e) {
    delete sch.validate;
    delete sch.validateName;
    if (sourceCode) this.logger.error("Error compiling schema, function code:", sourceCode);
    // console.log("\n\n\n *** \n", sourceCode, this.opts)
    throw e;
  } finally {
    this._compilations.delete(sch);
  }
}
compile.compileSchema = compileSchema;
function resolveRef(root, baseId, ref) {
  var _a;
  ref = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, ref);
  const schOrFunc = root.refs[ref];
  if (schOrFunc) return schOrFunc;
  let _sch = resolve$1.call(this, root, ref);
  if (_sch === undefined) {
    const schema = (_a = root.localRefs) === null || _a === void 0 ? void 0 : _a[ref]; // TODO maybe localRefs should hold SchemaEnv
    const {
      schemaId
    } = this.opts;
    if (schema) _sch = new SchemaEnv({
      schema,
      schemaId,
      root,
      baseId
    });
  }
  if (_sch === undefined) return;
  return root.refs[ref] = inlineOrCompile.call(this, _sch);
}
compile.resolveRef = resolveRef;
function inlineOrCompile(sch) {
  if ((0, resolve_1.inlineRef)(sch.schema, this.opts.inlineRefs)) return sch.schema;
  return sch.validate ? sch : compileSchema.call(this, sch);
}
// Index of schema compilation in the currently compiled list
function getCompilingSchema(schEnv) {
  for (const sch of this._compilations) {
    if (sameSchemaEnv(sch, schEnv)) return sch;
  }
}
compile.getCompilingSchema = getCompilingSchema;
function sameSchemaEnv(s1, s2) {
  return s1.schema === s2.schema && s1.root === s2.root && s1.baseId === s2.baseId;
}
// resolve and compile the references ($ref)
// TODO returns AnySchemaObject (if the schema can be inlined) or validation function
function resolve$1(root,
// information about the root schema for the current schema
ref // reference to resolve
) {
  let sch;
  while (typeof (sch = this.refs[ref]) == "string") ref = sch;
  return sch || this.schemas[ref] || resolveSchema.call(this, root, ref);
}
// Resolve schema, its root and baseId
function resolveSchema(root,
// root object with properties schema, refs TODO below SchemaEnv is assigned to it
ref // reference to resolve
) {
  const p = this.opts.uriResolver.parse(ref);
  const refPath = (0, resolve_1._getFullPath)(this.opts.uriResolver, p);
  let baseId = (0, resolve_1.getFullPath)(this.opts.uriResolver, root.baseId, undefined);
  // TODO `Object.keys(root.schema).length > 0` should not be needed - but removing breaks 2 tests
  if (Object.keys(root.schema).length > 0 && refPath === baseId) {
    return getJsonPointer.call(this, p, root);
  }
  const id = (0, resolve_1.normalizeId)(refPath);
  const schOrRef = this.refs[id] || this.schemas[id];
  if (typeof schOrRef == "string") {
    const sch = resolveSchema.call(this, root, schOrRef);
    if (typeof (sch === null || sch === void 0 ? void 0 : sch.schema) !== "object") return;
    return getJsonPointer.call(this, p, sch);
  }
  if (typeof (schOrRef === null || schOrRef === void 0 ? void 0 : schOrRef.schema) !== "object") return;
  if (!schOrRef.validate) compileSchema.call(this, schOrRef);
  if (id === (0, resolve_1.normalizeId)(ref)) {
    const {
      schema
    } = schOrRef;
    const {
      schemaId
    } = this.opts;
    const schId = schema[schemaId];
    if (schId) baseId = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, schId);
    return new SchemaEnv({
      schema,
      schemaId,
      root,
      baseId
    });
  }
  return getJsonPointer.call(this, p, schOrRef);
}
compile.resolveSchema = resolveSchema;
const PREVENT_SCOPE_CHANGE = new Set(["properties", "patternProperties", "enum", "dependencies", "definitions"]);
function getJsonPointer(parsedRef, {
  baseId,
  schema,
  root
}) {
  var _a;
  if (((_a = parsedRef.fragment) === null || _a === void 0 ? void 0 : _a[0]) !== "/") return;
  for (const part of parsedRef.fragment.slice(1).split("/")) {
    if (typeof schema === "boolean") return;
    const partSchema = schema[(0, util_1$k.unescapeFragment)(part)];
    if (partSchema === undefined) return;
    schema = partSchema;
    // TODO PREVENT_SCOPE_CHANGE could be defined in keyword def?
    const schId = typeof schema === "object" && schema[this.opts.schemaId];
    if (!PREVENT_SCOPE_CHANGE.has(part) && schId) {
      baseId = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, schId);
    }
  }
  let env;
  if (typeof schema != "boolean" && schema.$ref && !(0, util_1$k.schemaHasRulesButRef)(schema, this.RULES)) {
    const $ref = (0, resolve_1.resolveUrl)(this.opts.uriResolver, baseId, schema.$ref);
    env = resolveSchema.call(this, root, $ref);
  }
  // even though resolution failed we need to return SchemaEnv to throw exception
  // so that compileAsync loads missing schema.
  const {
    schemaId
  } = this.opts;
  env = env || new SchemaEnv({
    schema,
    schemaId,
    root,
    baseId
  });
  if (env.schema !== env.root.schema) return env;
  return undefined;
}

const $id$1 = "https://raw.githubusercontent.com/ajv-validator/ajv/master/lib/refs/data.json#";
const description = "Meta-schema for $data reference (JSON AnySchema extension proposal)";
const type$1 = "object";
const required$1 = [
	"$data"
];
const properties$2 = {
	$data: {
		type: "string",
		anyOf: [
			{
				format: "relative-json-pointer"
			},
			{
				format: "json-pointer"
			}
		]
	}
};
const additionalProperties$1 = false;
const require$$9 = {
	$id: $id$1,
	description: description,
	type: type$1,
	required: required$1,
	properties: properties$2,
	additionalProperties: additionalProperties$1
};

var uri$1 = {};

var fastUri$1 = {exports: {}};

const HEX$1 = {
  0: 0,
  1: 1,
  2: 2,
  3: 3,
  4: 4,
  5: 5,
  6: 6,
  7: 7,
  8: 8,
  9: 9,
  a: 10,
  A: 10,
  b: 11,
  B: 11,
  c: 12,
  C: 12,
  d: 13,
  D: 13,
  e: 14,
  E: 14,
  f: 15,
  F: 15
};
var scopedChars = {
  HEX: HEX$1
};

const {
  HEX
} = scopedChars;
function normalizeIPv4$1(host) {
  if (findToken(host, '.') < 3) {
    return {
      host,
      isIPV4: false
    };
  }
  const matches = host.match(/^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$/u) || [];
  const [address] = matches;
  if (address) {
    return {
      host: stripLeadingZeros(address, '.'),
      isIPV4: true
    };
  } else {
    return {
      host,
      isIPV4: false
    };
  }
}

/**
 * @param {string[]} input
 * @param {boolean} [keepZero=false]
 * @returns {string|undefined}
 */
function stringArrayToHexStripped(input, keepZero = false) {
  let acc = '';
  let strip = true;
  for (const c of input) {
    if (HEX[c] === undefined) return undefined;
    if (c !== '0' && strip === true) strip = false;
    if (!strip) acc += c;
  }
  if (keepZero && acc.length === 0) acc = '0';
  return acc;
}
function getIPV6(input) {
  let tokenCount = 0;
  const output = {
    error: false,
    address: '',
    zone: ''
  };
  const address = [];
  const buffer = [];
  let isZone = false;
  let endipv6Encountered = false;
  let endIpv6 = false;
  function consume() {
    if (buffer.length) {
      if (isZone === false) {
        const hex = stringArrayToHexStripped(buffer);
        if (hex !== undefined) {
          address.push(hex);
        } else {
          output.error = true;
          return false;
        }
      }
      buffer.length = 0;
    }
    return true;
  }
  for (let i = 0; i < input.length; i++) {
    const cursor = input[i];
    if (cursor === '[' || cursor === ']') {
      continue;
    }
    if (cursor === ':') {
      if (endipv6Encountered === true) {
        endIpv6 = true;
      }
      if (!consume()) {
        break;
      }
      tokenCount++;
      address.push(':');
      if (tokenCount > 7) {
        // not valid
        output.error = true;
        break;
      }
      if (i - 1 >= 0 && input[i - 1] === ':') {
        endipv6Encountered = true;
      }
      continue;
    } else if (cursor === '%') {
      if (!consume()) {
        break;
      }
      // switch to zone detection
      isZone = true;
    } else {
      buffer.push(cursor);
      continue;
    }
  }
  if (buffer.length) {
    if (isZone) {
      output.zone = buffer.join('');
    } else if (endIpv6) {
      address.push(buffer.join(''));
    } else {
      address.push(stringArrayToHexStripped(buffer));
    }
  }
  output.address = address.join('');
  return output;
}
function normalizeIPv6$1(host, opts = {}) {
  if (findToken(host, ':') < 2) {
    return {
      host,
      isIPV6: false
    };
  }
  const ipv6 = getIPV6(host);
  if (!ipv6.error) {
    let newHost = ipv6.address;
    let escapedHost = ipv6.address;
    if (ipv6.zone) {
      newHost += '%' + ipv6.zone;
      escapedHost += '%25' + ipv6.zone;
    }
    return {
      host: newHost,
      escapedHost,
      isIPV6: true
    };
  } else {
    return {
      host,
      isIPV6: false
    };
  }
}
function stripLeadingZeros(str, token) {
  let out = '';
  let skip = true;
  const l = str.length;
  for (let i = 0; i < l; i++) {
    const c = str[i];
    if (c === '0' && skip) {
      if (i + 1 <= l && str[i + 1] === token || i + 1 === l) {
        out += c;
        skip = false;
      }
    } else {
      if (c === token) {
        skip = true;
      } else {
        skip = false;
      }
      out += c;
    }
  }
  return out;
}
function findToken(str, token) {
  let ind = 0;
  for (let i = 0; i < str.length; i++) {
    if (str[i] === token) ind++;
  }
  return ind;
}
const RDS1 = /^\.\.?\//u;
const RDS2 = /^\/\.(?:\/|$)/u;
const RDS3 = /^\/\.\.(?:\/|$)/u;
const RDS5 = /^\/?(?:.|\n)*?(?=\/|$)/u;
function removeDotSegments$1(input) {
  const output = [];
  while (input.length) {
    if (input.match(RDS1)) {
      input = input.replace(RDS1, '');
    } else if (input.match(RDS2)) {
      input = input.replace(RDS2, '/');
    } else if (input.match(RDS3)) {
      input = input.replace(RDS3, '/');
      output.pop();
    } else if (input === '.' || input === '..') {
      input = '';
    } else {
      const im = input.match(RDS5);
      if (im) {
        const s = im[0];
        input = input.slice(s.length);
        output.push(s);
      } else {
        throw new Error('Unexpected dot segment condition');
      }
    }
  }
  return output.join('');
}
function normalizeComponentEncoding$1(components, esc) {
  const func = esc !== true ? escape : unescape;
  if (components.scheme !== undefined) {
    components.scheme = func(components.scheme);
  }
  if (components.userinfo !== undefined) {
    components.userinfo = func(components.userinfo);
  }
  if (components.host !== undefined) {
    components.host = func(components.host);
  }
  if (components.path !== undefined) {
    components.path = func(components.path);
  }
  if (components.query !== undefined) {
    components.query = func(components.query);
  }
  if (components.fragment !== undefined) {
    components.fragment = func(components.fragment);
  }
  return components;
}
function recomposeAuthority$1(components, options) {
  const uriTokens = [];
  if (components.userinfo !== undefined) {
    uriTokens.push(components.userinfo);
    uriTokens.push('@');
  }
  if (components.host !== undefined) {
    let host = unescape(components.host);
    const ipV4res = normalizeIPv4$1(host);
    if (ipV4res.isIPV4) {
      host = ipV4res.host;
    } else {
      const ipV6res = normalizeIPv6$1(ipV4res.host, {
        isIPV4: false
      });
      if (ipV6res.isIPV6 === true) {
        host = `[${ipV6res.escapedHost}]`;
      } else {
        host = components.host;
      }
    }
    uriTokens.push(host);
  }
  if (typeof components.port === 'number' || typeof components.port === 'string') {
    uriTokens.push(':');
    uriTokens.push(String(components.port));
  }
  return uriTokens.length ? uriTokens.join('') : undefined;
}
var utils = {
  recomposeAuthority: recomposeAuthority$1,
  normalizeComponentEncoding: normalizeComponentEncoding$1,
  removeDotSegments: removeDotSegments$1,
  normalizeIPv4: normalizeIPv4$1,
  normalizeIPv6: normalizeIPv6$1,
  stringArrayToHexStripped
};

const UUID_REG = /^[\da-f]{8}\b-[\da-f]{4}\b-[\da-f]{4}\b-[\da-f]{4}\b-[\da-f]{12}$/iu;
const URN_REG = /([\da-z][\d\-a-z]{0,31}):((?:[\w!$'()*+,\-.:;=@]|%[\da-f]{2})+)/iu;
function isSecure(wsComponents) {
  return typeof wsComponents.secure === 'boolean' ? wsComponents.secure : String(wsComponents.scheme).toLowerCase() === 'wss';
}
function httpParse(components) {
  if (!components.host) {
    components.error = components.error || 'HTTP URIs must have a host.';
  }
  return components;
}
function httpSerialize(components) {
  const secure = String(components.scheme).toLowerCase() === 'https';

  // normalize the default port
  if (components.port === (secure ? 443 : 80) || components.port === '') {
    components.port = undefined;
  }

  // normalize the empty path
  if (!components.path) {
    components.path = '/';
  }

  // NOTE: We do not parse query strings for HTTP URIs
  // as WWW Form Url Encoded query strings are part of the HTML4+ spec,
  // and not the HTTP spec.

  return components;
}
function wsParse(wsComponents) {
  // indicate if the secure flag is set
  wsComponents.secure = isSecure(wsComponents);

  // construct resouce name
  wsComponents.resourceName = (wsComponents.path || '/') + (wsComponents.query ? '?' + wsComponents.query : '');
  wsComponents.path = undefined;
  wsComponents.query = undefined;
  return wsComponents;
}
function wsSerialize(wsComponents) {
  // normalize the default port
  if (wsComponents.port === (isSecure(wsComponents) ? 443 : 80) || wsComponents.port === '') {
    wsComponents.port = undefined;
  }

  // ensure scheme matches secure flag
  if (typeof wsComponents.secure === 'boolean') {
    wsComponents.scheme = wsComponents.secure ? 'wss' : 'ws';
    wsComponents.secure = undefined;
  }

  // reconstruct path from resource name
  if (wsComponents.resourceName) {
    const [path, query] = wsComponents.resourceName.split('?');
    wsComponents.path = path && path !== '/' ? path : undefined;
    wsComponents.query = query;
    wsComponents.resourceName = undefined;
  }

  // forbid fragment component
  wsComponents.fragment = undefined;
  return wsComponents;
}
function urnParse(urnComponents, options) {
  if (!urnComponents.path) {
    urnComponents.error = 'URN can not be parsed';
    return urnComponents;
  }
  const matches = urnComponents.path.match(URN_REG);
  if (matches) {
    const scheme = options.scheme || urnComponents.scheme || 'urn';
    urnComponents.nid = matches[1].toLowerCase();
    urnComponents.nss = matches[2];
    const urnScheme = `${scheme}:${options.nid || urnComponents.nid}`;
    const schemeHandler = SCHEMES$1[urnScheme];
    urnComponents.path = undefined;
    if (schemeHandler) {
      urnComponents = schemeHandler.parse(urnComponents, options);
    }
  } else {
    urnComponents.error = urnComponents.error || 'URN can not be parsed.';
  }
  return urnComponents;
}
function urnSerialize(urnComponents, options) {
  const scheme = options.scheme || urnComponents.scheme || 'urn';
  const nid = urnComponents.nid.toLowerCase();
  const urnScheme = `${scheme}:${options.nid || nid}`;
  const schemeHandler = SCHEMES$1[urnScheme];
  if (schemeHandler) {
    urnComponents = schemeHandler.serialize(urnComponents, options);
  }
  const uriComponents = urnComponents;
  const nss = urnComponents.nss;
  uriComponents.path = `${nid || options.nid}:${nss}`;
  options.skipEscape = true;
  return uriComponents;
}
function urnuuidParse(urnComponents, options) {
  const uuidComponents = urnComponents;
  uuidComponents.uuid = uuidComponents.nss;
  uuidComponents.nss = undefined;
  if (!options.tolerant && (!uuidComponents.uuid || !UUID_REG.test(uuidComponents.uuid))) {
    uuidComponents.error = uuidComponents.error || 'UUID is not valid.';
  }
  return uuidComponents;
}
function urnuuidSerialize(uuidComponents) {
  const urnComponents = uuidComponents;
  // normalize UUID
  urnComponents.nss = (uuidComponents.uuid || '').toLowerCase();
  return urnComponents;
}
const http = {
  scheme: 'http',
  domainHost: true,
  parse: httpParse,
  serialize: httpSerialize
};
const https = {
  scheme: 'https',
  domainHost: http.domainHost,
  parse: httpParse,
  serialize: httpSerialize
};
const ws = {
  scheme: 'ws',
  domainHost: true,
  parse: wsParse,
  serialize: wsSerialize
};
const wss = {
  scheme: 'wss',
  domainHost: ws.domainHost,
  parse: ws.parse,
  serialize: ws.serialize
};
const urn = {
  scheme: 'urn',
  parse: urnParse,
  serialize: urnSerialize,
  skipNormalize: true
};
const urnuuid = {
  scheme: 'urn:uuid',
  parse: urnuuidParse,
  serialize: urnuuidSerialize,
  skipNormalize: true
};
const SCHEMES$1 = {
  http,
  https,
  ws,
  wss,
  urn,
  'urn:uuid': urnuuid
};
var schemes = SCHEMES$1;

const {
  normalizeIPv6,
  normalizeIPv4,
  removeDotSegments,
  recomposeAuthority,
  normalizeComponentEncoding
} = utils;
const SCHEMES = schemes;
function normalize$1(uri, options) {
  if (typeof uri === 'string') {
    uri = serialize(parse$1(uri, options), options);
  } else if (typeof uri === 'object') {
    uri = parse$1(serialize(uri, options), options);
  }
  return uri;
}
function resolve(baseURI, relativeURI, options) {
  const schemelessOptions = Object.assign({
    scheme: 'null'
  }, options);
  const resolved = resolveComponents(parse$1(baseURI, schemelessOptions), parse$1(relativeURI, schemelessOptions), schemelessOptions, true);
  return serialize(resolved, {
    ...schemelessOptions,
    skipEscape: true
  });
}
function resolveComponents(base, relative, options, skipNormalization) {
  const target = {};
  if (!skipNormalization) {
    base = parse$1(serialize(base, options), options); // normalize base components
    relative = parse$1(serialize(relative, options), options); // normalize relative components
  }
  options = options || {};
  if (!options.tolerant && relative.scheme) {
    target.scheme = relative.scheme;
    // target.authority = relative.authority;
    target.userinfo = relative.userinfo;
    target.host = relative.host;
    target.port = relative.port;
    target.path = removeDotSegments(relative.path || '');
    target.query = relative.query;
  } else {
    if (relative.userinfo !== undefined || relative.host !== undefined || relative.port !== undefined) {
      // target.authority = relative.authority;
      target.userinfo = relative.userinfo;
      target.host = relative.host;
      target.port = relative.port;
      target.path = removeDotSegments(relative.path || '');
      target.query = relative.query;
    } else {
      if (!relative.path) {
        target.path = base.path;
        if (relative.query !== undefined) {
          target.query = relative.query;
        } else {
          target.query = base.query;
        }
      } else {
        if (relative.path.charAt(0) === '/') {
          target.path = removeDotSegments(relative.path);
        } else {
          if ((base.userinfo !== undefined || base.host !== undefined || base.port !== undefined) && !base.path) {
            target.path = '/' + relative.path;
          } else if (!base.path) {
            target.path = relative.path;
          } else {
            target.path = base.path.slice(0, base.path.lastIndexOf('/') + 1) + relative.path;
          }
          target.path = removeDotSegments(target.path);
        }
        target.query = relative.query;
      }
      // target.authority = base.authority;
      target.userinfo = base.userinfo;
      target.host = base.host;
      target.port = base.port;
    }
    target.scheme = base.scheme;
  }
  target.fragment = relative.fragment;
  return target;
}
function equal$2(uriA, uriB, options) {
  if (typeof uriA === 'string') {
    uriA = unescape(uriA);
    uriA = serialize(normalizeComponentEncoding(parse$1(uriA, options), true), {
      ...options,
      skipEscape: true
    });
  } else if (typeof uriA === 'object') {
    uriA = serialize(normalizeComponentEncoding(uriA, true), {
      ...options,
      skipEscape: true
    });
  }
  if (typeof uriB === 'string') {
    uriB = unescape(uriB);
    uriB = serialize(normalizeComponentEncoding(parse$1(uriB, options), true), {
      ...options,
      skipEscape: true
    });
  } else if (typeof uriB === 'object') {
    uriB = serialize(normalizeComponentEncoding(uriB, true), {
      ...options,
      skipEscape: true
    });
  }
  return uriA.toLowerCase() === uriB.toLowerCase();
}
function serialize(cmpts, opts) {
  const components = {
    host: cmpts.host,
    scheme: cmpts.scheme,
    userinfo: cmpts.userinfo,
    port: cmpts.port,
    path: cmpts.path,
    query: cmpts.query,
    nid: cmpts.nid,
    nss: cmpts.nss,
    uuid: cmpts.uuid,
    fragment: cmpts.fragment,
    reference: cmpts.reference,
    resourceName: cmpts.resourceName,
    secure: cmpts.secure,
    error: ''
  };
  const options = Object.assign({}, opts);
  const uriTokens = [];

  // find scheme handler
  const schemeHandler = SCHEMES[(options.scheme || components.scheme || '').toLowerCase()];

  // perform scheme specific serialization
  if (schemeHandler && schemeHandler.serialize) schemeHandler.serialize(components, options);
  if (components.path !== undefined) {
    if (!options.skipEscape) {
      components.path = escape(components.path);
      if (components.scheme !== undefined) {
        components.path = components.path.split('%3A').join(':');
      }
    } else {
      components.path = unescape(components.path);
    }
  }
  if (options.reference !== 'suffix' && components.scheme) {
    uriTokens.push(components.scheme);
    uriTokens.push(':');
  }
  const authority = recomposeAuthority(components, options);
  if (authority !== undefined) {
    if (options.reference !== 'suffix') {
      uriTokens.push('//');
    }
    uriTokens.push(authority);
    if (components.path && components.path.charAt(0) !== '/') {
      uriTokens.push('/');
    }
  }
  if (components.path !== undefined) {
    let s = components.path;
    if (!options.absolutePath && (!schemeHandler || !schemeHandler.absolutePath)) {
      s = removeDotSegments(s);
    }
    if (authority === undefined) {
      s = s.replace(/^\/\//u, '/%2F'); // don't allow the path to start with "//"
    }
    uriTokens.push(s);
  }
  if (components.query !== undefined) {
    uriTokens.push('?');
    uriTokens.push(components.query);
  }
  if (components.fragment !== undefined) {
    uriTokens.push('#');
    uriTokens.push(components.fragment);
  }
  return uriTokens.join('');
}
const hexLookUp = Array.from({
  length: 127
}, (v, k) => /[^!"$&'()*+,\-.;=_`a-z{}~]/u.test(String.fromCharCode(k)));
function nonSimpleDomain(value) {
  let code = 0;
  for (let i = 0, len = value.length; i < len; ++i) {
    code = value.charCodeAt(i);
    if (code > 126 || hexLookUp[code]) {
      return true;
    }
  }
  return false;
}
const URI_PARSE = /^(?:([^#/:?]+):)?(?:\/\/((?:([^#/?@]*)@)?(\[[^#/?\]]+\]|[^#/:?]*)(?::(\d*))?))?([^#?]*)(?:\?([^#]*))?(?:#((?:.|[\n\r])*))?/u;
function parse$1(uri, opts) {
  const options = Object.assign({}, opts);
  const parsed = {
    scheme: undefined,
    userinfo: undefined,
    host: '',
    port: undefined,
    path: '',
    query: undefined,
    fragment: undefined
  };
  const gotEncoding = uri.indexOf('%') !== -1;
  let isIP = false;
  if (options.reference === 'suffix') uri = (options.scheme ? options.scheme + ':' : '') + '//' + uri;
  const matches = uri.match(URI_PARSE);
  if (matches) {
    // store each component
    parsed.scheme = matches[1];
    parsed.userinfo = matches[3];
    parsed.host = matches[4];
    parsed.port = parseInt(matches[5], 10);
    parsed.path = matches[6] || '';
    parsed.query = matches[7];
    parsed.fragment = matches[8];

    // fix port number
    if (isNaN(parsed.port)) {
      parsed.port = matches[5];
    }
    if (parsed.host) {
      const ipv4result = normalizeIPv4(parsed.host);
      if (ipv4result.isIPV4 === false) {
        const ipv6result = normalizeIPv6(ipv4result.host, {
          isIPV4: false
        });
        parsed.host = ipv6result.host.toLowerCase();
        isIP = ipv6result.isIPV6;
      } else {
        parsed.host = ipv4result.host;
        isIP = true;
      }
    }
    if (parsed.scheme === undefined && parsed.userinfo === undefined && parsed.host === undefined && parsed.port === undefined && !parsed.path && parsed.query === undefined) {
      parsed.reference = 'same-document';
    } else if (parsed.scheme === undefined) {
      parsed.reference = 'relative';
    } else if (parsed.fragment === undefined) {
      parsed.reference = 'absolute';
    } else {
      parsed.reference = 'uri';
    }

    // check for reference errors
    if (options.reference && options.reference !== 'suffix' && options.reference !== parsed.reference) {
      parsed.error = parsed.error || 'URI is not a ' + options.reference + ' reference.';
    }

    // find scheme handler
    const schemeHandler = SCHEMES[(options.scheme || parsed.scheme || '').toLowerCase()];

    // check if scheme can't handle IRIs
    if (!options.unicodeSupport && (!schemeHandler || !schemeHandler.unicodeSupport)) {
      // if host component is a domain name
      if (parsed.host && (options.domainHost || schemeHandler && schemeHandler.domainHost) && isIP === false && nonSimpleDomain(parsed.host)) {
        // convert Unicode IDN -> ASCII IDN
        try {
          parsed.host = URL.domainToASCII(parsed.host.toLowerCase());
        } catch (e) {
          parsed.error = parsed.error || "Host's domain name can not be converted to ASCII: " + e;
        }
      }
      // convert IRI -> URI
    }
    if (!schemeHandler || schemeHandler && !schemeHandler.skipNormalize) {
      if (gotEncoding && parsed.scheme !== undefined) {
        parsed.scheme = unescape(parsed.scheme);
      }
      if (gotEncoding && parsed.userinfo !== undefined) {
        parsed.userinfo = unescape(parsed.userinfo);
      }
      if (gotEncoding && parsed.host !== undefined) {
        parsed.host = unescape(parsed.host);
      }
      if (parsed.path !== undefined && parsed.path.length) {
        parsed.path = escape(unescape(parsed.path));
      }
      if (parsed.fragment !== undefined && parsed.fragment.length) {
        parsed.fragment = encodeURI(decodeURIComponent(parsed.fragment));
      }
    }

    // perform scheme specific parsing
    if (schemeHandler && schemeHandler.parse) {
      schemeHandler.parse(parsed, options);
    }
  } else {
    parsed.error = parsed.error || 'URI can not be parsed.';
  }
  return parsed;
}
const fastUri = {
  SCHEMES,
  normalize: normalize$1,
  resolve,
  resolveComponents,
  equal: equal$2,
  serialize,
  parse: parse$1
};
fastUri$1.exports = fastUri;
fastUri$1.exports.default = fastUri;
fastUri$1.exports.fastUri = fastUri;

var fastUriExports = fastUri$1.exports;

Object.defineProperty(uri$1, "__esModule", {
  value: true
});
const uri = fastUriExports;
uri.code = 'require("ajv/dist/runtime/uri").default';
uri$1.default = uri;

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.CodeGen = exports.Name = exports.nil = exports.stringify = exports.str = exports._ = exports.KeywordCxt = void 0;
	var validate_1 = validate;
	Object.defineProperty(exports, "KeywordCxt", {
	  enumerable: true,
	  get: function () {
	    return validate_1.KeywordCxt;
	  }
	});
	var codegen_1 = codegen;
	Object.defineProperty(exports, "_", {
	  enumerable: true,
	  get: function () {
	    return codegen_1._;
	  }
	});
	Object.defineProperty(exports, "str", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.str;
	  }
	});
	Object.defineProperty(exports, "stringify", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.stringify;
	  }
	});
	Object.defineProperty(exports, "nil", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.nil;
	  }
	});
	Object.defineProperty(exports, "Name", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.Name;
	  }
	});
	Object.defineProperty(exports, "CodeGen", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.CodeGen;
	  }
	});
	const validation_error_1 = validation_error;
	const ref_error_1 = ref_error;
	const rules_1 = rules;
	const compile_1 = compile;
	const codegen_2 = codegen;
	const resolve_1 = resolve$2;
	const dataType_1 = dataType;
	const util_1 = util;
	const $dataRefSchema = require$$9;
	const uri_1 = uri$1;
	const defaultRegExp = (str, flags) => new RegExp(str, flags);
	defaultRegExp.code = "new RegExp";
	const META_IGNORE_OPTIONS = ["removeAdditional", "useDefaults", "coerceTypes"];
	const EXT_SCOPE_NAMES = new Set(["validate", "serialize", "parse", "wrapper", "root", "schema", "keyword", "pattern", "formats", "validate$data", "func", "obj", "Error"]);
	const removedOptions = {
	  errorDataPath: "",
	  format: "`validateFormats: false` can be used instead.",
	  nullable: '"nullable" keyword is supported by default.',
	  jsonPointers: "Deprecated jsPropertySyntax can be used instead.",
	  extendRefs: "Deprecated ignoreKeywordsWithRef can be used instead.",
	  missingRefs: "Pass empty schema with $id that should be ignored to ajv.addSchema.",
	  processCode: "Use option `code: {process: (code, schemaEnv: object) => string}`",
	  sourceCode: "Use option `code: {source: true}`",
	  strictDefaults: "It is default now, see option `strict`.",
	  strictKeywords: "It is default now, see option `strict`.",
	  uniqueItems: '"uniqueItems" keyword is always validated.',
	  unknownFormats: "Disable strict mode or pass `true` to `ajv.addFormat` (or `formats` option).",
	  cache: "Map is used as cache, schema object as key.",
	  serialize: "Map is used as cache, schema object as key.",
	  ajvErrors: "It is default now."
	};
	const deprecatedOptions = {
	  ignoreKeywordsWithRef: "",
	  jsPropertySyntax: "",
	  unicode: '"minLength"/"maxLength" account for unicode characters by default.'
	};
	const MAX_EXPRESSION = 200;
	// eslint-disable-next-line complexity
	function requiredOptions(o) {
	  var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p, _q, _r, _s, _t, _u, _v, _w, _x, _y, _z, _0;
	  const s = o.strict;
	  const _optz = (_a = o.code) === null || _a === void 0 ? void 0 : _a.optimize;
	  const optimize = _optz === true || _optz === undefined ? 1 : _optz || 0;
	  const regExp = (_c = (_b = o.code) === null || _b === void 0 ? void 0 : _b.regExp) !== null && _c !== void 0 ? _c : defaultRegExp;
	  const uriResolver = (_d = o.uriResolver) !== null && _d !== void 0 ? _d : uri_1.default;
	  return {
	    strictSchema: (_f = (_e = o.strictSchema) !== null && _e !== void 0 ? _e : s) !== null && _f !== void 0 ? _f : true,
	    strictNumbers: (_h = (_g = o.strictNumbers) !== null && _g !== void 0 ? _g : s) !== null && _h !== void 0 ? _h : true,
	    strictTypes: (_k = (_j = o.strictTypes) !== null && _j !== void 0 ? _j : s) !== null && _k !== void 0 ? _k : "log",
	    strictTuples: (_m = (_l = o.strictTuples) !== null && _l !== void 0 ? _l : s) !== null && _m !== void 0 ? _m : "log",
	    strictRequired: (_p = (_o = o.strictRequired) !== null && _o !== void 0 ? _o : s) !== null && _p !== void 0 ? _p : false,
	    code: o.code ? {
	      ...o.code,
	      optimize,
	      regExp
	    } : {
	      optimize,
	      regExp
	    },
	    loopRequired: (_q = o.loopRequired) !== null && _q !== void 0 ? _q : MAX_EXPRESSION,
	    loopEnum: (_r = o.loopEnum) !== null && _r !== void 0 ? _r : MAX_EXPRESSION,
	    meta: (_s = o.meta) !== null && _s !== void 0 ? _s : true,
	    messages: (_t = o.messages) !== null && _t !== void 0 ? _t : true,
	    inlineRefs: (_u = o.inlineRefs) !== null && _u !== void 0 ? _u : true,
	    schemaId: (_v = o.schemaId) !== null && _v !== void 0 ? _v : "$id",
	    addUsedSchema: (_w = o.addUsedSchema) !== null && _w !== void 0 ? _w : true,
	    validateSchema: (_x = o.validateSchema) !== null && _x !== void 0 ? _x : true,
	    validateFormats: (_y = o.validateFormats) !== null && _y !== void 0 ? _y : true,
	    unicodeRegExp: (_z = o.unicodeRegExp) !== null && _z !== void 0 ? _z : true,
	    int32range: (_0 = o.int32range) !== null && _0 !== void 0 ? _0 : true,
	    uriResolver: uriResolver
	  };
	}
	class Ajv {
	  constructor(opts = {}) {
	    this.schemas = {};
	    this.refs = {};
	    this.formats = {};
	    this._compilations = new Set();
	    this._loading = {};
	    this._cache = new Map();
	    opts = this.opts = {
	      ...opts,
	      ...requiredOptions(opts)
	    };
	    const {
	      es5,
	      lines
	    } = this.opts.code;
	    this.scope = new codegen_2.ValueScope({
	      scope: {},
	      prefixes: EXT_SCOPE_NAMES,
	      es5,
	      lines
	    });
	    this.logger = getLogger(opts.logger);
	    const formatOpt = opts.validateFormats;
	    opts.validateFormats = false;
	    this.RULES = (0, rules_1.getRules)();
	    checkOptions.call(this, removedOptions, opts, "NOT SUPPORTED");
	    checkOptions.call(this, deprecatedOptions, opts, "DEPRECATED", "warn");
	    this._metaOpts = getMetaSchemaOptions.call(this);
	    if (opts.formats) addInitialFormats.call(this);
	    this._addVocabularies();
	    this._addDefaultMetaSchema();
	    if (opts.keywords) addInitialKeywords.call(this, opts.keywords);
	    if (typeof opts.meta == "object") this.addMetaSchema(opts.meta);
	    addInitialSchemas.call(this);
	    opts.validateFormats = formatOpt;
	  }
	  _addVocabularies() {
	    this.addKeyword("$async");
	  }
	  _addDefaultMetaSchema() {
	    const {
	      $data,
	      meta,
	      schemaId
	    } = this.opts;
	    let _dataRefSchema = $dataRefSchema;
	    if (schemaId === "id") {
	      _dataRefSchema = {
	        ...$dataRefSchema
	      };
	      _dataRefSchema.id = _dataRefSchema.$id;
	      delete _dataRefSchema.$id;
	    }
	    if (meta && $data) this.addMetaSchema(_dataRefSchema, _dataRefSchema[schemaId], false);
	  }
	  defaultMeta() {
	    const {
	      meta,
	      schemaId
	    } = this.opts;
	    return this.opts.defaultMeta = typeof meta == "object" ? meta[schemaId] || meta : undefined;
	  }
	  validate(schemaKeyRef,
	  // key, ref or schema object
	  // eslint-disable-next-line @typescript-eslint/no-redundant-type-constituents
	  data // to be validated
	  ) {
	    let v;
	    if (typeof schemaKeyRef == "string") {
	      v = this.getSchema(schemaKeyRef);
	      if (!v) throw new Error(`no schema with key or ref "${schemaKeyRef}"`);
	    } else {
	      v = this.compile(schemaKeyRef);
	    }
	    const valid = v(data);
	    if (!("$async" in v)) this.errors = v.errors;
	    return valid;
	  }
	  compile(schema, _meta) {
	    const sch = this._addSchema(schema, _meta);
	    return sch.validate || this._compileSchemaEnv(sch);
	  }
	  compileAsync(schema, meta) {
	    if (typeof this.opts.loadSchema != "function") {
	      throw new Error("options.loadSchema should be a function");
	    }
	    const {
	      loadSchema
	    } = this.opts;
	    return runCompileAsync.call(this, schema, meta);
	    async function runCompileAsync(_schema, _meta) {
	      await loadMetaSchema.call(this, _schema.$schema);
	      const sch = this._addSchema(_schema, _meta);
	      return sch.validate || _compileAsync.call(this, sch);
	    }
	    async function loadMetaSchema($ref) {
	      if ($ref && !this.getSchema($ref)) {
	        await runCompileAsync.call(this, {
	          $ref
	        }, true);
	      }
	    }
	    async function _compileAsync(sch) {
	      try {
	        return this._compileSchemaEnv(sch);
	      } catch (e) {
	        if (!(e instanceof ref_error_1.default)) throw e;
	        checkLoaded.call(this, e);
	        await loadMissingSchema.call(this, e.missingSchema);
	        return _compileAsync.call(this, sch);
	      }
	    }
	    function checkLoaded({
	      missingSchema: ref,
	      missingRef
	    }) {
	      if (this.refs[ref]) {
	        throw new Error(`AnySchema ${ref} is loaded but ${missingRef} cannot be resolved`);
	      }
	    }
	    async function loadMissingSchema(ref) {
	      const _schema = await _loadSchema.call(this, ref);
	      if (!this.refs[ref]) await loadMetaSchema.call(this, _schema.$schema);
	      if (!this.refs[ref]) this.addSchema(_schema, ref, meta);
	    }
	    async function _loadSchema(ref) {
	      const p = this._loading[ref];
	      if (p) return p;
	      try {
	        return await (this._loading[ref] = loadSchema(ref));
	      } finally {
	        delete this._loading[ref];
	      }
	    }
	  }
	  // Adds schema to the instance
	  addSchema(schema,
	  // If array is passed, `key` will be ignored
	  key,
	  // Optional schema key. Can be passed to `validate` method instead of schema object or id/ref. One schema per instance can have empty `id` and `key`.
	  _meta,
	  // true if schema is a meta-schema. Used internally, addMetaSchema should be used instead.
	  _validateSchema = this.opts.validateSchema // false to skip schema validation. Used internally, option validateSchema should be used instead.
	  ) {
	    if (Array.isArray(schema)) {
	      for (const sch of schema) this.addSchema(sch, undefined, _meta, _validateSchema);
	      return this;
	    }
	    let id;
	    if (typeof schema === "object") {
	      const {
	        schemaId
	      } = this.opts;
	      id = schema[schemaId];
	      if (id !== undefined && typeof id != "string") {
	        throw new Error(`schema ${schemaId} must be string`);
	      }
	    }
	    key = (0, resolve_1.normalizeId)(key || id);
	    this._checkUnique(key);
	    this.schemas[key] = this._addSchema(schema, _meta, key, _validateSchema, true);
	    return this;
	  }
	  // Add schema that will be used to validate other schemas
	  // options in META_IGNORE_OPTIONS are alway set to false
	  addMetaSchema(schema, key,
	  // schema key
	  _validateSchema = this.opts.validateSchema // false to skip schema validation, can be used to override validateSchema option for meta-schema
	  ) {
	    this.addSchema(schema, key, true, _validateSchema);
	    return this;
	  }
	  //  Validate schema against its meta-schema
	  validateSchema(schema, throwOrLogError) {
	    if (typeof schema == "boolean") return true;
	    let $schema;
	    $schema = schema.$schema;
	    if ($schema !== undefined && typeof $schema != "string") {
	      throw new Error("$schema must be a string");
	    }
	    $schema = $schema || this.opts.defaultMeta || this.defaultMeta();
	    if (!$schema) {
	      this.logger.warn("meta-schema not available");
	      this.errors = null;
	      return true;
	    }
	    const valid = this.validate($schema, schema);
	    if (!valid && throwOrLogError) {
	      const message = "schema is invalid: " + this.errorsText();
	      if (this.opts.validateSchema === "log") this.logger.error(message);else throw new Error(message);
	    }
	    return valid;
	  }
	  // Get compiled schema by `key` or `ref`.
	  // (`key` that was passed to `addSchema` or full schema reference - `schema.$id` or resolved id)
	  getSchema(keyRef) {
	    let sch;
	    while (typeof (sch = getSchEnv.call(this, keyRef)) == "string") keyRef = sch;
	    if (sch === undefined) {
	      const {
	        schemaId
	      } = this.opts;
	      const root = new compile_1.SchemaEnv({
	        schema: {},
	        schemaId
	      });
	      sch = compile_1.resolveSchema.call(this, root, keyRef);
	      if (!sch) return;
	      this.refs[keyRef] = sch;
	    }
	    return sch.validate || this._compileSchemaEnv(sch);
	  }
	  // Remove cached schema(s).
	  // If no parameter is passed all schemas but meta-schemas are removed.
	  // If RegExp is passed all schemas with key/id matching pattern but meta-schemas are removed.
	  // Even if schema is referenced by other schemas it still can be removed as other schemas have local references.
	  removeSchema(schemaKeyRef) {
	    if (schemaKeyRef instanceof RegExp) {
	      this._removeAllSchemas(this.schemas, schemaKeyRef);
	      this._removeAllSchemas(this.refs, schemaKeyRef);
	      return this;
	    }
	    switch (typeof schemaKeyRef) {
	      case "undefined":
	        this._removeAllSchemas(this.schemas);
	        this._removeAllSchemas(this.refs);
	        this._cache.clear();
	        return this;
	      case "string":
	        {
	          const sch = getSchEnv.call(this, schemaKeyRef);
	          if (typeof sch == "object") this._cache.delete(sch.schema);
	          delete this.schemas[schemaKeyRef];
	          delete this.refs[schemaKeyRef];
	          return this;
	        }
	      case "object":
	        {
	          const cacheKey = schemaKeyRef;
	          this._cache.delete(cacheKey);
	          let id = schemaKeyRef[this.opts.schemaId];
	          if (id) {
	            id = (0, resolve_1.normalizeId)(id);
	            delete this.schemas[id];
	            delete this.refs[id];
	          }
	          return this;
	        }
	      default:
	        throw new Error("ajv.removeSchema: invalid parameter");
	    }
	  }
	  // add "vocabulary" - a collection of keywords
	  addVocabulary(definitions) {
	    for (const def of definitions) this.addKeyword(def);
	    return this;
	  }
	  addKeyword(kwdOrDef, def // deprecated
	  ) {
	    let keyword;
	    if (typeof kwdOrDef == "string") {
	      keyword = kwdOrDef;
	      if (typeof def == "object") {
	        this.logger.warn("these parameters are deprecated, see docs for addKeyword");
	        def.keyword = keyword;
	      }
	    } else if (typeof kwdOrDef == "object" && def === undefined) {
	      def = kwdOrDef;
	      keyword = def.keyword;
	      if (Array.isArray(keyword) && !keyword.length) {
	        throw new Error("addKeywords: keyword must be string or non-empty array");
	      }
	    } else {
	      throw new Error("invalid addKeywords parameters");
	    }
	    checkKeyword.call(this, keyword, def);
	    if (!def) {
	      (0, util_1.eachItem)(keyword, kwd => addRule.call(this, kwd));
	      return this;
	    }
	    keywordMetaschema.call(this, def);
	    const definition = {
	      ...def,
	      type: (0, dataType_1.getJSONTypes)(def.type),
	      schemaType: (0, dataType_1.getJSONTypes)(def.schemaType)
	    };
	    (0, util_1.eachItem)(keyword, definition.type.length === 0 ? k => addRule.call(this, k, definition) : k => definition.type.forEach(t => addRule.call(this, k, definition, t)));
	    return this;
	  }
	  getKeyword(keyword) {
	    const rule = this.RULES.all[keyword];
	    return typeof rule == "object" ? rule.definition : !!rule;
	  }
	  // Remove keyword
	  removeKeyword(keyword) {
	    // TODO return type should be Ajv
	    const {
	      RULES
	    } = this;
	    delete RULES.keywords[keyword];
	    delete RULES.all[keyword];
	    for (const group of RULES.rules) {
	      const i = group.rules.findIndex(rule => rule.keyword === keyword);
	      if (i >= 0) group.rules.splice(i, 1);
	    }
	    return this;
	  }
	  // Add format
	  addFormat(name, format) {
	    if (typeof format == "string") format = new RegExp(format);
	    this.formats[name] = format;
	    return this;
	  }
	  errorsText(errors = this.errors,
	  // optional array of validation errors
	  {
	    separator = ", ",
	    dataVar = "data"
	  } = {} // optional options with properties `separator` and `dataVar`
	  ) {
	    if (!errors || errors.length === 0) return "No errors";
	    return errors.map(e => `${dataVar}${e.instancePath} ${e.message}`).reduce((text, msg) => text + separator + msg);
	  }
	  $dataMetaSchema(metaSchema, keywordsJsonPointers) {
	    const rules = this.RULES.all;
	    metaSchema = JSON.parse(JSON.stringify(metaSchema));
	    for (const jsonPointer of keywordsJsonPointers) {
	      const segments = jsonPointer.split("/").slice(1); // first segment is an empty string
	      let keywords = metaSchema;
	      for (const seg of segments) keywords = keywords[seg];
	      for (const key in rules) {
	        const rule = rules[key];
	        if (typeof rule != "object") continue;
	        const {
	          $data
	        } = rule.definition;
	        const schema = keywords[key];
	        if ($data && schema) keywords[key] = schemaOrData(schema);
	      }
	    }
	    return metaSchema;
	  }
	  _removeAllSchemas(schemas, regex) {
	    for (const keyRef in schemas) {
	      const sch = schemas[keyRef];
	      if (!regex || regex.test(keyRef)) {
	        if (typeof sch == "string") {
	          delete schemas[keyRef];
	        } else if (sch && !sch.meta) {
	          this._cache.delete(sch.schema);
	          delete schemas[keyRef];
	        }
	      }
	    }
	  }
	  _addSchema(schema, meta, baseId, validateSchema = this.opts.validateSchema, addSchema = this.opts.addUsedSchema) {
	    let id;
	    const {
	      schemaId
	    } = this.opts;
	    if (typeof schema == "object") {
	      id = schema[schemaId];
	    } else {
	      if (this.opts.jtd) throw new Error("schema must be object");else if (typeof schema != "boolean") throw new Error("schema must be object or boolean");
	    }
	    let sch = this._cache.get(schema);
	    if (sch !== undefined) return sch;
	    baseId = (0, resolve_1.normalizeId)(id || baseId);
	    const localRefs = resolve_1.getSchemaRefs.call(this, schema, baseId);
	    sch = new compile_1.SchemaEnv({
	      schema,
	      schemaId,
	      meta,
	      baseId,
	      localRefs
	    });
	    this._cache.set(sch.schema, sch);
	    if (addSchema && !baseId.startsWith("#")) {
	      // TODO atm it is allowed to overwrite schemas without id (instead of not adding them)
	      if (baseId) this._checkUnique(baseId);
	      this.refs[baseId] = sch;
	    }
	    if (validateSchema) this.validateSchema(schema, true);
	    return sch;
	  }
	  _checkUnique(id) {
	    if (this.schemas[id] || this.refs[id]) {
	      throw new Error(`schema with key or id "${id}" already exists`);
	    }
	  }
	  _compileSchemaEnv(sch) {
	    if (sch.meta) this._compileMetaSchema(sch);else compile_1.compileSchema.call(this, sch);
	    /* istanbul ignore if */
	    if (!sch.validate) throw new Error("ajv implementation error");
	    return sch.validate;
	  }
	  _compileMetaSchema(sch) {
	    const currentOpts = this.opts;
	    this.opts = this._metaOpts;
	    try {
	      compile_1.compileSchema.call(this, sch);
	    } finally {
	      this.opts = currentOpts;
	    }
	  }
	}
	Ajv.ValidationError = validation_error_1.default;
	Ajv.MissingRefError = ref_error_1.default;
	exports.default = Ajv;
	function checkOptions(checkOpts, options, msg, log = "error") {
	  for (const key in checkOpts) {
	    const opt = key;
	    if (opt in options) this.logger[log](`${msg}: option ${key}. ${checkOpts[opt]}`);
	  }
	}
	function getSchEnv(keyRef) {
	  keyRef = (0, resolve_1.normalizeId)(keyRef); // TODO tests fail without this line
	  return this.schemas[keyRef] || this.refs[keyRef];
	}
	function addInitialSchemas() {
	  const optsSchemas = this.opts.schemas;
	  if (!optsSchemas) return;
	  if (Array.isArray(optsSchemas)) this.addSchema(optsSchemas);else for (const key in optsSchemas) this.addSchema(optsSchemas[key], key);
	}
	function addInitialFormats() {
	  for (const name in this.opts.formats) {
	    const format = this.opts.formats[name];
	    if (format) this.addFormat(name, format);
	  }
	}
	function addInitialKeywords(defs) {
	  if (Array.isArray(defs)) {
	    this.addVocabulary(defs);
	    return;
	  }
	  this.logger.warn("keywords option as map is deprecated, pass array");
	  for (const keyword in defs) {
	    const def = defs[keyword];
	    if (!def.keyword) def.keyword = keyword;
	    this.addKeyword(def);
	  }
	}
	function getMetaSchemaOptions() {
	  const metaOpts = {
	    ...this.opts
	  };
	  for (const opt of META_IGNORE_OPTIONS) delete metaOpts[opt];
	  return metaOpts;
	}
	const noLogs = {
	  log() {},
	  warn() {},
	  error() {}
	};
	function getLogger(logger) {
	  if (logger === false) return noLogs;
	  if (logger === undefined) return console;
	  if (logger.log && logger.warn && logger.error) return logger;
	  throw new Error("logger must implement log, warn and error methods");
	}
	const KEYWORD_NAME = /^[a-z_$][a-z0-9_$:-]*$/i;
	function checkKeyword(keyword, def) {
	  const {
	    RULES
	  } = this;
	  (0, util_1.eachItem)(keyword, kwd => {
	    if (RULES.keywords[kwd]) throw new Error(`Keyword ${kwd} is already defined`);
	    if (!KEYWORD_NAME.test(kwd)) throw new Error(`Keyword ${kwd} has invalid name`);
	  });
	  if (!def) return;
	  if (def.$data && !("code" in def || "validate" in def)) {
	    throw new Error('$data keyword must have "code" or "validate" function');
	  }
	}
	function addRule(keyword, definition, dataType) {
	  var _a;
	  const post = definition === null || definition === void 0 ? void 0 : definition.post;
	  if (dataType && post) throw new Error('keyword with "post" flag cannot have "type"');
	  const {
	    RULES
	  } = this;
	  let ruleGroup = post ? RULES.post : RULES.rules.find(({
	    type: t
	  }) => t === dataType);
	  if (!ruleGroup) {
	    ruleGroup = {
	      type: dataType,
	      rules: []
	    };
	    RULES.rules.push(ruleGroup);
	  }
	  RULES.keywords[keyword] = true;
	  if (!definition) return;
	  const rule = {
	    keyword,
	    definition: {
	      ...definition,
	      type: (0, dataType_1.getJSONTypes)(definition.type),
	      schemaType: (0, dataType_1.getJSONTypes)(definition.schemaType)
	    }
	  };
	  if (definition.before) addBeforeRule.call(this, ruleGroup, rule, definition.before);else ruleGroup.rules.push(rule);
	  RULES.all[keyword] = rule;
	  (_a = definition.implements) === null || _a === void 0 ? void 0 : _a.forEach(kwd => this.addKeyword(kwd));
	}
	function addBeforeRule(ruleGroup, rule, before) {
	  const i = ruleGroup.rules.findIndex(_rule => _rule.keyword === before);
	  if (i >= 0) {
	    ruleGroup.rules.splice(i, 0, rule);
	  } else {
	    ruleGroup.rules.push(rule);
	    this.logger.warn(`rule ${before} is not defined`);
	  }
	}
	function keywordMetaschema(def) {
	  let {
	    metaSchema
	  } = def;
	  if (metaSchema === undefined) return;
	  if (def.$data && this.opts.$data) metaSchema = schemaOrData(metaSchema);
	  def.validateSchema = this.compile(metaSchema, true);
	}
	const $dataRef = {
	  $ref: "https://raw.githubusercontent.com/ajv-validator/ajv/master/lib/refs/data.json#"
	};
	function schemaOrData(schema) {
	  return {
	    anyOf: [schema, $dataRef]
	  };
	} 
} (core$2));

var draft7 = {};

var core$1 = {};

var id = {};

Object.defineProperty(id, "__esModule", {
  value: true
});
const def$s = {
  keyword: "id",
  code() {
    throw new Error('NOT SUPPORTED: keyword "id", use "$id" for schema ID');
  }
};
id.default = def$s;

var ref = {};

Object.defineProperty(ref, "__esModule", {
  value: true
});
ref.callRef = ref.getValidate = void 0;
const ref_error_1$1 = ref_error;
const code_1$8 = code;
const codegen_1$l = codegen;
const names_1$1 = names$1;
const compile_1$1 = compile;
const util_1$j = util;
const def$r = {
  keyword: "$ref",
  schemaType: "string",
  code(cxt) {
    const {
      gen,
      schema: $ref,
      it
    } = cxt;
    const {
      baseId,
      schemaEnv: env,
      validateName,
      opts,
      self
    } = it;
    const {
      root
    } = env;
    if (($ref === "#" || $ref === "#/") && baseId === root.baseId) return callRootRef();
    const schOrEnv = compile_1$1.resolveRef.call(self, root, baseId, $ref);
    if (schOrEnv === undefined) throw new ref_error_1$1.default(it.opts.uriResolver, baseId, $ref);
    if (schOrEnv instanceof compile_1$1.SchemaEnv) return callValidate(schOrEnv);
    return inlineRefSchema(schOrEnv);
    function callRootRef() {
      if (env === root) return callRef(cxt, validateName, env, env.$async);
      const rootName = gen.scopeValue("root", {
        ref: root
      });
      return callRef(cxt, (0, codegen_1$l._)`${rootName}.validate`, root, root.$async);
    }
    function callValidate(sch) {
      const v = getValidate(cxt, sch);
      callRef(cxt, v, sch, sch.$async);
    }
    function inlineRefSchema(sch) {
      const schName = gen.scopeValue("schema", opts.code.source === true ? {
        ref: sch,
        code: (0, codegen_1$l.stringify)(sch)
      } : {
        ref: sch
      });
      const valid = gen.name("valid");
      const schCxt = cxt.subschema({
        schema: sch,
        dataTypes: [],
        schemaPath: codegen_1$l.nil,
        topSchemaRef: schName,
        errSchemaPath: $ref
      }, valid);
      cxt.mergeEvaluated(schCxt);
      cxt.ok(valid);
    }
  }
};
function getValidate(cxt, sch) {
  const {
    gen
  } = cxt;
  return sch.validate ? gen.scopeValue("validate", {
    ref: sch.validate
  }) : (0, codegen_1$l._)`${gen.scopeValue("wrapper", {
    ref: sch
  })}.validate`;
}
ref.getValidate = getValidate;
function callRef(cxt, v, sch, $async) {
  const {
    gen,
    it
  } = cxt;
  const {
    allErrors,
    schemaEnv: env,
    opts
  } = it;
  const passCxt = opts.passContext ? names_1$1.default.this : codegen_1$l.nil;
  if ($async) callAsyncRef();else callSyncRef();
  function callAsyncRef() {
    if (!env.$async) throw new Error("async schema referenced by sync schema");
    const valid = gen.let("valid");
    gen.try(() => {
      gen.code((0, codegen_1$l._)`await ${(0, code_1$8.callValidateCode)(cxt, v, passCxt)}`);
      addEvaluatedFrom(v); // TODO will not work with async, it has to be returned with the result
      if (!allErrors) gen.assign(valid, true);
    }, e => {
      gen.if((0, codegen_1$l._)`!(${e} instanceof ${it.ValidationError})`, () => gen.throw(e));
      addErrorsFrom(e);
      if (!allErrors) gen.assign(valid, false);
    });
    cxt.ok(valid);
  }
  function callSyncRef() {
    cxt.result((0, code_1$8.callValidateCode)(cxt, v, passCxt), () => addEvaluatedFrom(v), () => addErrorsFrom(v));
  }
  function addErrorsFrom(source) {
    const errs = (0, codegen_1$l._)`${source}.errors`;
    gen.assign(names_1$1.default.vErrors, (0, codegen_1$l._)`${names_1$1.default.vErrors} === null ? ${errs} : ${names_1$1.default.vErrors}.concat(${errs})`); // TODO tagged
    gen.assign(names_1$1.default.errors, (0, codegen_1$l._)`${names_1$1.default.vErrors}.length`);
  }
  function addEvaluatedFrom(source) {
    var _a;
    if (!it.opts.unevaluated) return;
    const schEvaluated = (_a = sch === null || sch === void 0 ? void 0 : sch.validate) === null || _a === void 0 ? void 0 : _a.evaluated;
    // TODO refactor
    if (it.props !== true) {
      if (schEvaluated && !schEvaluated.dynamicProps) {
        if (schEvaluated.props !== undefined) {
          it.props = util_1$j.mergeEvaluated.props(gen, schEvaluated.props, it.props);
        }
      } else {
        const props = gen.var("props", (0, codegen_1$l._)`${source}.evaluated.props`);
        it.props = util_1$j.mergeEvaluated.props(gen, props, it.props, codegen_1$l.Name);
      }
    }
    if (it.items !== true) {
      if (schEvaluated && !schEvaluated.dynamicItems) {
        if (schEvaluated.items !== undefined) {
          it.items = util_1$j.mergeEvaluated.items(gen, schEvaluated.items, it.items);
        }
      } else {
        const items = gen.var("items", (0, codegen_1$l._)`${source}.evaluated.items`);
        it.items = util_1$j.mergeEvaluated.items(gen, items, it.items, codegen_1$l.Name);
      }
    }
  }
}
ref.callRef = callRef;
ref.default = def$r;

Object.defineProperty(core$1, "__esModule", {
  value: true
});
const id_1 = id;
const ref_1 = ref;
const core = ["$schema", "$id", "$defs", "$vocabulary", {
  keyword: "$comment"
}, "definitions", id_1.default, ref_1.default];
core$1.default = core;

var validation$1 = {};

var limitNumber = {};

Object.defineProperty(limitNumber, "__esModule", {
  value: true
});
const codegen_1$k = codegen;
const ops = codegen_1$k.operators;
const KWDs = {
  maximum: {
    okStr: "<=",
    ok: ops.LTE,
    fail: ops.GT
  },
  minimum: {
    okStr: ">=",
    ok: ops.GTE,
    fail: ops.LT
  },
  exclusiveMaximum: {
    okStr: "<",
    ok: ops.LT,
    fail: ops.GTE
  },
  exclusiveMinimum: {
    okStr: ">",
    ok: ops.GT,
    fail: ops.LTE
  }
};
const error$j = {
  message: ({
    keyword,
    schemaCode
  }) => (0, codegen_1$k.str)`must be ${KWDs[keyword].okStr} ${schemaCode}`,
  params: ({
    keyword,
    schemaCode
  }) => (0, codegen_1$k._)`{comparison: ${KWDs[keyword].okStr}, limit: ${schemaCode}}`
};
const def$q = {
  keyword: Object.keys(KWDs),
  type: "number",
  schemaType: "number",
  $data: true,
  error: error$j,
  code(cxt) {
    const {
      keyword,
      data,
      schemaCode
    } = cxt;
    cxt.fail$data((0, codegen_1$k._)`${data} ${KWDs[keyword].fail} ${schemaCode} || isNaN(${data})`);
  }
};
limitNumber.default = def$q;

var multipleOf = {};

Object.defineProperty(multipleOf, "__esModule", {
  value: true
});
const codegen_1$j = codegen;
const error$i = {
  message: ({
    schemaCode
  }) => (0, codegen_1$j.str)`must be multiple of ${schemaCode}`,
  params: ({
    schemaCode
  }) => (0, codegen_1$j._)`{multipleOf: ${schemaCode}}`
};
const def$p = {
  keyword: "multipleOf",
  type: "number",
  schemaType: "number",
  $data: true,
  error: error$i,
  code(cxt) {
    const {
      gen,
      data,
      schemaCode,
      it
    } = cxt;
    // const bdt = bad$DataType(schemaCode, <string>def.schemaType, $data)
    const prec = it.opts.multipleOfPrecision;
    const res = gen.let("res");
    const invalid = prec ? (0, codegen_1$j._)`Math.abs(Math.round(${res}) - ${res}) > 1e-${prec}` : (0, codegen_1$j._)`${res} !== parseInt(${res})`;
    cxt.fail$data((0, codegen_1$j._)`(${schemaCode} === 0 || (${res} = ${data}/${schemaCode}, ${invalid}))`);
  }
};
multipleOf.default = def$p;

var limitLength = {};

var ucs2length$1 = {};

Object.defineProperty(ucs2length$1, "__esModule", {
  value: true
});
// https://mathiasbynens.be/notes/javascript-encoding
// https://github.com/bestiejs/punycode.js - punycode.ucs2.decode
function ucs2length(str) {
  const len = str.length;
  let length = 0;
  let pos = 0;
  let value;
  while (pos < len) {
    length++;
    value = str.charCodeAt(pos++);
    if (value >= 0xd800 && value <= 0xdbff && pos < len) {
      // high surrogate, and there is a next character
      value = str.charCodeAt(pos);
      if ((value & 0xfc00) === 0xdc00) pos++; // low surrogate
    }
  }
  return length;
}
ucs2length$1.default = ucs2length;
ucs2length.code = 'require("ajv/dist/runtime/ucs2length").default';

Object.defineProperty(limitLength, "__esModule", {
  value: true
});
const codegen_1$i = codegen;
const util_1$i = util;
const ucs2length_1 = ucs2length$1;
const error$h = {
  message({
    keyword,
    schemaCode
  }) {
    const comp = keyword === "maxLength" ? "more" : "fewer";
    return (0, codegen_1$i.str)`must NOT have ${comp} than ${schemaCode} characters`;
  },
  params: ({
    schemaCode
  }) => (0, codegen_1$i._)`{limit: ${schemaCode}}`
};
const def$o = {
  keyword: ["maxLength", "minLength"],
  type: "string",
  schemaType: "number",
  $data: true,
  error: error$h,
  code(cxt) {
    const {
      keyword,
      data,
      schemaCode,
      it
    } = cxt;
    const op = keyword === "maxLength" ? codegen_1$i.operators.GT : codegen_1$i.operators.LT;
    const len = it.opts.unicode === false ? (0, codegen_1$i._)`${data}.length` : (0, codegen_1$i._)`${(0, util_1$i.useFunc)(cxt.gen, ucs2length_1.default)}(${data})`;
    cxt.fail$data((0, codegen_1$i._)`${len} ${op} ${schemaCode}`);
  }
};
limitLength.default = def$o;

var pattern = {};

Object.defineProperty(pattern, "__esModule", {
  value: true
});
const code_1$7 = code;
const codegen_1$h = codegen;
const error$g = {
  message: ({
    schemaCode
  }) => (0, codegen_1$h.str)`must match pattern "${schemaCode}"`,
  params: ({
    schemaCode
  }) => (0, codegen_1$h._)`{pattern: ${schemaCode}}`
};
const def$n = {
  keyword: "pattern",
  type: "string",
  schemaType: "string",
  $data: true,
  error: error$g,
  code(cxt) {
    const {
      data,
      $data,
      schema,
      schemaCode,
      it
    } = cxt;
    // TODO regexp should be wrapped in try/catchs
    const u = it.opts.unicodeRegExp ? "u" : "";
    const regExp = $data ? (0, codegen_1$h._)`(new RegExp(${schemaCode}, ${u}))` : (0, code_1$7.usePattern)(cxt, schema);
    cxt.fail$data((0, codegen_1$h._)`!${regExp}.test(${data})`);
  }
};
pattern.default = def$n;

var limitProperties = {};

Object.defineProperty(limitProperties, "__esModule", {
  value: true
});
const codegen_1$g = codegen;
const error$f = {
  message({
    keyword,
    schemaCode
  }) {
    const comp = keyword === "maxProperties" ? "more" : "fewer";
    return (0, codegen_1$g.str)`must NOT have ${comp} than ${schemaCode} properties`;
  },
  params: ({
    schemaCode
  }) => (0, codegen_1$g._)`{limit: ${schemaCode}}`
};
const def$m = {
  keyword: ["maxProperties", "minProperties"],
  type: "object",
  schemaType: "number",
  $data: true,
  error: error$f,
  code(cxt) {
    const {
      keyword,
      data,
      schemaCode
    } = cxt;
    const op = keyword === "maxProperties" ? codegen_1$g.operators.GT : codegen_1$g.operators.LT;
    cxt.fail$data((0, codegen_1$g._)`Object.keys(${data}).length ${op} ${schemaCode}`);
  }
};
limitProperties.default = def$m;

var required = {};

Object.defineProperty(required, "__esModule", {
  value: true
});
const code_1$6 = code;
const codegen_1$f = codegen;
const util_1$h = util;
const error$e = {
  message: ({
    params: {
      missingProperty
    }
  }) => (0, codegen_1$f.str)`must have required property '${missingProperty}'`,
  params: ({
    params: {
      missingProperty
    }
  }) => (0, codegen_1$f._)`{missingProperty: ${missingProperty}}`
};
const def$l = {
  keyword: "required",
  type: "object",
  schemaType: "array",
  $data: true,
  error: error$e,
  code(cxt) {
    const {
      gen,
      schema,
      schemaCode,
      data,
      $data,
      it
    } = cxt;
    const {
      opts
    } = it;
    if (!$data && schema.length === 0) return;
    const useLoop = schema.length >= opts.loopRequired;
    if (it.allErrors) allErrorsMode();else exitOnErrorMode();
    if (opts.strictRequired) {
      const props = cxt.parentSchema.properties;
      const {
        definedProperties
      } = cxt.it;
      for (const requiredKey of schema) {
        if ((props === null || props === void 0 ? void 0 : props[requiredKey]) === undefined && !definedProperties.has(requiredKey)) {
          const schemaPath = it.schemaEnv.baseId + it.errSchemaPath;
          const msg = `required property "${requiredKey}" is not defined at "${schemaPath}" (strictRequired)`;
          (0, util_1$h.checkStrictMode)(it, msg, it.opts.strictRequired);
        }
      }
    }
    function allErrorsMode() {
      if (useLoop || $data) {
        cxt.block$data(codegen_1$f.nil, loopAllRequired);
      } else {
        for (const prop of schema) {
          (0, code_1$6.checkReportMissingProp)(cxt, prop);
        }
      }
    }
    function exitOnErrorMode() {
      const missing = gen.let("missing");
      if (useLoop || $data) {
        const valid = gen.let("valid", true);
        cxt.block$data(valid, () => loopUntilMissing(missing, valid));
        cxt.ok(valid);
      } else {
        gen.if((0, code_1$6.checkMissingProp)(cxt, schema, missing));
        (0, code_1$6.reportMissingProp)(cxt, missing);
        gen.else();
      }
    }
    function loopAllRequired() {
      gen.forOf("prop", schemaCode, prop => {
        cxt.setParams({
          missingProperty: prop
        });
        gen.if((0, code_1$6.noPropertyInData)(gen, data, prop, opts.ownProperties), () => cxt.error());
      });
    }
    function loopUntilMissing(missing, valid) {
      cxt.setParams({
        missingProperty: missing
      });
      gen.forOf(missing, schemaCode, () => {
        gen.assign(valid, (0, code_1$6.propertyInData)(gen, data, missing, opts.ownProperties));
        gen.if((0, codegen_1$f.not)(valid), () => {
          cxt.error();
          gen.break();
        });
      }, codegen_1$f.nil);
    }
  }
};
required.default = def$l;

var limitItems = {};

Object.defineProperty(limitItems, "__esModule", {
  value: true
});
const codegen_1$e = codegen;
const error$d = {
  message({
    keyword,
    schemaCode
  }) {
    const comp = keyword === "maxItems" ? "more" : "fewer";
    return (0, codegen_1$e.str)`must NOT have ${comp} than ${schemaCode} items`;
  },
  params: ({
    schemaCode
  }) => (0, codegen_1$e._)`{limit: ${schemaCode}}`
};
const def$k = {
  keyword: ["maxItems", "minItems"],
  type: "array",
  schemaType: "number",
  $data: true,
  error: error$d,
  code(cxt) {
    const {
      keyword,
      data,
      schemaCode
    } = cxt;
    const op = keyword === "maxItems" ? codegen_1$e.operators.GT : codegen_1$e.operators.LT;
    cxt.fail$data((0, codegen_1$e._)`${data}.length ${op} ${schemaCode}`);
  }
};
limitItems.default = def$k;

var uniqueItems = {};

var equal$1 = {};

Object.defineProperty(equal$1, "__esModule", {
  value: true
});
// https://github.com/ajv-validator/ajv/issues/889
const equal = fastDeepEqual;
equal.code = 'require("ajv/dist/runtime/equal").default';
equal$1.default = equal;

Object.defineProperty(uniqueItems, "__esModule", {
  value: true
});
const dataType_1 = dataType;
const codegen_1$d = codegen;
const util_1$g = util;
const equal_1$2 = equal$1;
const error$c = {
  message: ({
    params: {
      i,
      j
    }
  }) => (0, codegen_1$d.str)`must NOT have duplicate items (items ## ${j} and ${i} are identical)`,
  params: ({
    params: {
      i,
      j
    }
  }) => (0, codegen_1$d._)`{i: ${i}, j: ${j}}`
};
const def$j = {
  keyword: "uniqueItems",
  type: "array",
  schemaType: "boolean",
  $data: true,
  error: error$c,
  code(cxt) {
    const {
      gen,
      data,
      $data,
      schema,
      parentSchema,
      schemaCode,
      it
    } = cxt;
    if (!$data && !schema) return;
    const valid = gen.let("valid");
    const itemTypes = parentSchema.items ? (0, dataType_1.getSchemaTypes)(parentSchema.items) : [];
    cxt.block$data(valid, validateUniqueItems, (0, codegen_1$d._)`${schemaCode} === false`);
    cxt.ok(valid);
    function validateUniqueItems() {
      const i = gen.let("i", (0, codegen_1$d._)`${data}.length`);
      const j = gen.let("j");
      cxt.setParams({
        i,
        j
      });
      gen.assign(valid, true);
      gen.if((0, codegen_1$d._)`${i} > 1`, () => (canOptimize() ? loopN : loopN2)(i, j));
    }
    function canOptimize() {
      return itemTypes.length > 0 && !itemTypes.some(t => t === "object" || t === "array");
    }
    function loopN(i, j) {
      const item = gen.name("item");
      const wrongType = (0, dataType_1.checkDataTypes)(itemTypes, item, it.opts.strictNumbers, dataType_1.DataType.Wrong);
      const indices = gen.const("indices", (0, codegen_1$d._)`{}`);
      gen.for((0, codegen_1$d._)`;${i}--;`, () => {
        gen.let(item, (0, codegen_1$d._)`${data}[${i}]`);
        gen.if(wrongType, (0, codegen_1$d._)`continue`);
        if (itemTypes.length > 1) gen.if((0, codegen_1$d._)`typeof ${item} == "string"`, (0, codegen_1$d._)`${item} += "_"`);
        gen.if((0, codegen_1$d._)`typeof ${indices}[${item}] == "number"`, () => {
          gen.assign(j, (0, codegen_1$d._)`${indices}[${item}]`);
          cxt.error();
          gen.assign(valid, false).break();
        }).code((0, codegen_1$d._)`${indices}[${item}] = ${i}`);
      });
    }
    function loopN2(i, j) {
      const eql = (0, util_1$g.useFunc)(gen, equal_1$2.default);
      const outer = gen.name("outer");
      gen.label(outer).for((0, codegen_1$d._)`;${i}--;`, () => gen.for((0, codegen_1$d._)`${j} = ${i}; ${j}--;`, () => gen.if((0, codegen_1$d._)`${eql}(${data}[${i}], ${data}[${j}])`, () => {
        cxt.error();
        gen.assign(valid, false).break(outer);
      })));
    }
  }
};
uniqueItems.default = def$j;

var _const = {};

Object.defineProperty(_const, "__esModule", {
  value: true
});
const codegen_1$c = codegen;
const util_1$f = util;
const equal_1$1 = equal$1;
const error$b = {
  message: "must be equal to constant",
  params: ({
    schemaCode
  }) => (0, codegen_1$c._)`{allowedValue: ${schemaCode}}`
};
const def$i = {
  keyword: "const",
  $data: true,
  error: error$b,
  code(cxt) {
    const {
      gen,
      data,
      $data,
      schemaCode,
      schema
    } = cxt;
    if ($data || schema && typeof schema == "object") {
      cxt.fail$data((0, codegen_1$c._)`!${(0, util_1$f.useFunc)(gen, equal_1$1.default)}(${data}, ${schemaCode})`);
    } else {
      cxt.fail((0, codegen_1$c._)`${schema} !== ${data}`);
    }
  }
};
_const.default = def$i;

var _enum = {};

Object.defineProperty(_enum, "__esModule", {
  value: true
});
const codegen_1$b = codegen;
const util_1$e = util;
const equal_1 = equal$1;
const error$a = {
  message: "must be equal to one of the allowed values",
  params: ({
    schemaCode
  }) => (0, codegen_1$b._)`{allowedValues: ${schemaCode}}`
};
const def$h = {
  keyword: "enum",
  schemaType: "array",
  $data: true,
  error: error$a,
  code(cxt) {
    const {
      gen,
      data,
      $data,
      schema,
      schemaCode,
      it
    } = cxt;
    if (!$data && schema.length === 0) throw new Error("enum must have non-empty array");
    const useLoop = schema.length >= it.opts.loopEnum;
    let eql;
    const getEql = () => eql !== null && eql !== void 0 ? eql : eql = (0, util_1$e.useFunc)(gen, equal_1.default);
    let valid;
    if (useLoop || $data) {
      valid = gen.let("valid");
      cxt.block$data(valid, loopEnum);
    } else {
      /* istanbul ignore if */
      if (!Array.isArray(schema)) throw new Error("ajv implementation error");
      const vSchema = gen.const("vSchema", schemaCode);
      valid = (0, codegen_1$b.or)(...schema.map((_x, i) => equalCode(vSchema, i)));
    }
    cxt.pass(valid);
    function loopEnum() {
      gen.assign(valid, false);
      gen.forOf("v", schemaCode, v => gen.if((0, codegen_1$b._)`${getEql()}(${data}, ${v})`, () => gen.assign(valid, true).break()));
    }
    function equalCode(vSchema, i) {
      const sch = schema[i];
      return typeof sch === "object" && sch !== null ? (0, codegen_1$b._)`${getEql()}(${data}, ${vSchema}[${i}])` : (0, codegen_1$b._)`${data} === ${sch}`;
    }
  }
};
_enum.default = def$h;

Object.defineProperty(validation$1, "__esModule", {
  value: true
});
const limitNumber_1 = limitNumber;
const multipleOf_1 = multipleOf;
const limitLength_1 = limitLength;
const pattern_1 = pattern;
const limitProperties_1 = limitProperties;
const required_1 = required;
const limitItems_1 = limitItems;
const uniqueItems_1 = uniqueItems;
const const_1 = _const;
const enum_1 = _enum;
const validation = [
// number
limitNumber_1.default, multipleOf_1.default,
// string
limitLength_1.default, pattern_1.default,
// object
limitProperties_1.default, required_1.default,
// array
limitItems_1.default, uniqueItems_1.default,
// any
{
  keyword: "type",
  schemaType: ["string", "array"]
}, {
  keyword: "nullable",
  schemaType: "boolean"
}, const_1.default, enum_1.default];
validation$1.default = validation;

var applicator = {};

var additionalItems = {};

Object.defineProperty(additionalItems, "__esModule", {
  value: true
});
additionalItems.validateAdditionalItems = void 0;
const codegen_1$a = codegen;
const util_1$d = util;
const error$9 = {
  message: ({
    params: {
      len
    }
  }) => (0, codegen_1$a.str)`must NOT have more than ${len} items`,
  params: ({
    params: {
      len
    }
  }) => (0, codegen_1$a._)`{limit: ${len}}`
};
const def$g = {
  keyword: "additionalItems",
  type: "array",
  schemaType: ["boolean", "object"],
  before: "uniqueItems",
  error: error$9,
  code(cxt) {
    const {
      parentSchema,
      it
    } = cxt;
    const {
      items
    } = parentSchema;
    if (!Array.isArray(items)) {
      (0, util_1$d.checkStrictMode)(it, '"additionalItems" is ignored when "items" is not an array of schemas');
      return;
    }
    validateAdditionalItems(cxt, items);
  }
};
function validateAdditionalItems(cxt, items) {
  const {
    gen,
    schema,
    data,
    keyword,
    it
  } = cxt;
  it.items = true;
  const len = gen.const("len", (0, codegen_1$a._)`${data}.length`);
  if (schema === false) {
    cxt.setParams({
      len: items.length
    });
    cxt.pass((0, codegen_1$a._)`${len} <= ${items.length}`);
  } else if (typeof schema == "object" && !(0, util_1$d.alwaysValidSchema)(it, schema)) {
    const valid = gen.var("valid", (0, codegen_1$a._)`${len} <= ${items.length}`); // TODO var
    gen.if((0, codegen_1$a.not)(valid), () => validateItems(valid));
    cxt.ok(valid);
  }
  function validateItems(valid) {
    gen.forRange("i", items.length, len, i => {
      cxt.subschema({
        keyword,
        dataProp: i,
        dataPropType: util_1$d.Type.Num
      }, valid);
      if (!it.allErrors) gen.if((0, codegen_1$a.not)(valid), () => gen.break());
    });
  }
}
additionalItems.validateAdditionalItems = validateAdditionalItems;
additionalItems.default = def$g;

var prefixItems = {};

var items = {};

Object.defineProperty(items, "__esModule", {
  value: true
});
items.validateTuple = void 0;
const codegen_1$9 = codegen;
const util_1$c = util;
const code_1$5 = code;
const def$f = {
  keyword: "items",
  type: "array",
  schemaType: ["object", "array", "boolean"],
  before: "uniqueItems",
  code(cxt) {
    const {
      schema,
      it
    } = cxt;
    if (Array.isArray(schema)) return validateTuple(cxt, "additionalItems", schema);
    it.items = true;
    if ((0, util_1$c.alwaysValidSchema)(it, schema)) return;
    cxt.ok((0, code_1$5.validateArray)(cxt));
  }
};
function validateTuple(cxt, extraItems, schArr = cxt.schema) {
  const {
    gen,
    parentSchema,
    data,
    keyword,
    it
  } = cxt;
  checkStrictTuple(parentSchema);
  if (it.opts.unevaluated && schArr.length && it.items !== true) {
    it.items = util_1$c.mergeEvaluated.items(gen, schArr.length, it.items);
  }
  const valid = gen.name("valid");
  const len = gen.const("len", (0, codegen_1$9._)`${data}.length`);
  schArr.forEach((sch, i) => {
    if ((0, util_1$c.alwaysValidSchema)(it, sch)) return;
    gen.if((0, codegen_1$9._)`${len} > ${i}`, () => cxt.subschema({
      keyword,
      schemaProp: i,
      dataProp: i
    }, valid));
    cxt.ok(valid);
  });
  function checkStrictTuple(sch) {
    const {
      opts,
      errSchemaPath
    } = it;
    const l = schArr.length;
    const fullTuple = l === sch.minItems && (l === sch.maxItems || sch[extraItems] === false);
    if (opts.strictTuples && !fullTuple) {
      const msg = `"${keyword}" is ${l}-tuple, but minItems or maxItems/${extraItems} are not specified or different at path "${errSchemaPath}"`;
      (0, util_1$c.checkStrictMode)(it, msg, opts.strictTuples);
    }
  }
}
items.validateTuple = validateTuple;
items.default = def$f;

Object.defineProperty(prefixItems, "__esModule", {
  value: true
});
const items_1$1 = items;
const def$e = {
  keyword: "prefixItems",
  type: "array",
  schemaType: ["array"],
  before: "uniqueItems",
  code: cxt => (0, items_1$1.validateTuple)(cxt, "items")
};
prefixItems.default = def$e;

var items2020 = {};

Object.defineProperty(items2020, "__esModule", {
  value: true
});
const codegen_1$8 = codegen;
const util_1$b = util;
const code_1$4 = code;
const additionalItems_1$1 = additionalItems;
const error$8 = {
  message: ({
    params: {
      len
    }
  }) => (0, codegen_1$8.str)`must NOT have more than ${len} items`,
  params: ({
    params: {
      len
    }
  }) => (0, codegen_1$8._)`{limit: ${len}}`
};
const def$d = {
  keyword: "items",
  type: "array",
  schemaType: ["object", "boolean"],
  before: "uniqueItems",
  error: error$8,
  code(cxt) {
    const {
      schema,
      parentSchema,
      it
    } = cxt;
    const {
      prefixItems
    } = parentSchema;
    it.items = true;
    if ((0, util_1$b.alwaysValidSchema)(it, schema)) return;
    if (prefixItems) (0, additionalItems_1$1.validateAdditionalItems)(cxt, prefixItems);else cxt.ok((0, code_1$4.validateArray)(cxt));
  }
};
items2020.default = def$d;

var contains = {};

Object.defineProperty(contains, "__esModule", {
  value: true
});
const codegen_1$7 = codegen;
const util_1$a = util;
const error$7 = {
  message: ({
    params: {
      min,
      max
    }
  }) => max === undefined ? (0, codegen_1$7.str)`must contain at least ${min} valid item(s)` : (0, codegen_1$7.str)`must contain at least ${min} and no more than ${max} valid item(s)`,
  params: ({
    params: {
      min,
      max
    }
  }) => max === undefined ? (0, codegen_1$7._)`{minContains: ${min}}` : (0, codegen_1$7._)`{minContains: ${min}, maxContains: ${max}}`
};
const def$c = {
  keyword: "contains",
  type: "array",
  schemaType: ["object", "boolean"],
  before: "uniqueItems",
  trackErrors: true,
  error: error$7,
  code(cxt) {
    const {
      gen,
      schema,
      parentSchema,
      data,
      it
    } = cxt;
    let min;
    let max;
    const {
      minContains,
      maxContains
    } = parentSchema;
    if (it.opts.next) {
      min = minContains === undefined ? 1 : minContains;
      max = maxContains;
    } else {
      min = 1;
    }
    const len = gen.const("len", (0, codegen_1$7._)`${data}.length`);
    cxt.setParams({
      min,
      max
    });
    if (max === undefined && min === 0) {
      (0, util_1$a.checkStrictMode)(it, `"minContains" == 0 without "maxContains": "contains" keyword ignored`);
      return;
    }
    if (max !== undefined && min > max) {
      (0, util_1$a.checkStrictMode)(it, `"minContains" > "maxContains" is always invalid`);
      cxt.fail();
      return;
    }
    if ((0, util_1$a.alwaysValidSchema)(it, schema)) {
      let cond = (0, codegen_1$7._)`${len} >= ${min}`;
      if (max !== undefined) cond = (0, codegen_1$7._)`${cond} && ${len} <= ${max}`;
      cxt.pass(cond);
      return;
    }
    it.items = true;
    const valid = gen.name("valid");
    if (max === undefined && min === 1) {
      validateItems(valid, () => gen.if(valid, () => gen.break()));
    } else if (min === 0) {
      gen.let(valid, true);
      if (max !== undefined) gen.if((0, codegen_1$7._)`${data}.length > 0`, validateItemsWithCount);
    } else {
      gen.let(valid, false);
      validateItemsWithCount();
    }
    cxt.result(valid, () => cxt.reset());
    function validateItemsWithCount() {
      const schValid = gen.name("_valid");
      const count = gen.let("count", 0);
      validateItems(schValid, () => gen.if(schValid, () => checkLimits(count)));
    }
    function validateItems(_valid, block) {
      gen.forRange("i", 0, len, i => {
        cxt.subschema({
          keyword: "contains",
          dataProp: i,
          dataPropType: util_1$a.Type.Num,
          compositeRule: true
        }, _valid);
        block();
      });
    }
    function checkLimits(count) {
      gen.code((0, codegen_1$7._)`${count}++`);
      if (max === undefined) {
        gen.if((0, codegen_1$7._)`${count} >= ${min}`, () => gen.assign(valid, true).break());
      } else {
        gen.if((0, codegen_1$7._)`${count} > ${max}`, () => gen.assign(valid, false).break());
        if (min === 1) gen.assign(valid, true);else gen.if((0, codegen_1$7._)`${count} >= ${min}`, () => gen.assign(valid, true));
      }
    }
  }
};
contains.default = def$c;

var dependencies = {};

(function (exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.validateSchemaDeps = exports.validatePropertyDeps = exports.error = void 0;
	const codegen_1 = codegen;
	const util_1 = util;
	const code_1 = code;
	exports.error = {
	  message: ({
	    params: {
	      property,
	      depsCount,
	      deps
	    }
	  }) => {
	    const property_ies = depsCount === 1 ? "property" : "properties";
	    return (0, codegen_1.str)`must have ${property_ies} ${deps} when property ${property} is present`;
	  },
	  params: ({
	    params: {
	      property,
	      depsCount,
	      deps,
	      missingProperty
	    }
	  }) => (0, codegen_1._)`{property: ${property},
    missingProperty: ${missingProperty},
    depsCount: ${depsCount},
    deps: ${deps}}` // TODO change to reference
	};
	const def = {
	  keyword: "dependencies",
	  type: "object",
	  schemaType: "object",
	  error: exports.error,
	  code(cxt) {
	    const [propDeps, schDeps] = splitDependencies(cxt);
	    validatePropertyDeps(cxt, propDeps);
	    validateSchemaDeps(cxt, schDeps);
	  }
	};
	function splitDependencies({
	  schema
	}) {
	  const propertyDeps = {};
	  const schemaDeps = {};
	  for (const key in schema) {
	    if (key === "__proto__") continue;
	    const deps = Array.isArray(schema[key]) ? propertyDeps : schemaDeps;
	    deps[key] = schema[key];
	  }
	  return [propertyDeps, schemaDeps];
	}
	function validatePropertyDeps(cxt, propertyDeps = cxt.schema) {
	  const {
	    gen,
	    data,
	    it
	  } = cxt;
	  if (Object.keys(propertyDeps).length === 0) return;
	  const missing = gen.let("missing");
	  for (const prop in propertyDeps) {
	    const deps = propertyDeps[prop];
	    if (deps.length === 0) continue;
	    const hasProperty = (0, code_1.propertyInData)(gen, data, prop, it.opts.ownProperties);
	    cxt.setParams({
	      property: prop,
	      depsCount: deps.length,
	      deps: deps.join(", ")
	    });
	    if (it.allErrors) {
	      gen.if(hasProperty, () => {
	        for (const depProp of deps) {
	          (0, code_1.checkReportMissingProp)(cxt, depProp);
	        }
	      });
	    } else {
	      gen.if((0, codegen_1._)`${hasProperty} && (${(0, code_1.checkMissingProp)(cxt, deps, missing)})`);
	      (0, code_1.reportMissingProp)(cxt, missing);
	      gen.else();
	    }
	  }
	}
	exports.validatePropertyDeps = validatePropertyDeps;
	function validateSchemaDeps(cxt, schemaDeps = cxt.schema) {
	  const {
	    gen,
	    data,
	    keyword,
	    it
	  } = cxt;
	  const valid = gen.name("valid");
	  for (const prop in schemaDeps) {
	    if ((0, util_1.alwaysValidSchema)(it, schemaDeps[prop])) continue;
	    gen.if((0, code_1.propertyInData)(gen, data, prop, it.opts.ownProperties), () => {
	      const schCxt = cxt.subschema({
	        keyword,
	        schemaProp: prop
	      }, valid);
	      cxt.mergeValidEvaluated(schCxt, valid);
	    }, () => gen.var(valid, true) // TODO var
	    );
	    cxt.ok(valid);
	  }
	}
	exports.validateSchemaDeps = validateSchemaDeps;
	exports.default = def; 
} (dependencies));

var propertyNames = {};

Object.defineProperty(propertyNames, "__esModule", {
  value: true
});
const codegen_1$6 = codegen;
const util_1$9 = util;
const error$6 = {
  message: "property name must be valid",
  params: ({
    params
  }) => (0, codegen_1$6._)`{propertyName: ${params.propertyName}}`
};
const def$b = {
  keyword: "propertyNames",
  type: "object",
  schemaType: ["object", "boolean"],
  error: error$6,
  code(cxt) {
    const {
      gen,
      schema,
      data,
      it
    } = cxt;
    if ((0, util_1$9.alwaysValidSchema)(it, schema)) return;
    const valid = gen.name("valid");
    gen.forIn("key", data, key => {
      cxt.setParams({
        propertyName: key
      });
      cxt.subschema({
        keyword: "propertyNames",
        data: key,
        dataTypes: ["string"],
        propertyName: key,
        compositeRule: true
      }, valid);
      gen.if((0, codegen_1$6.not)(valid), () => {
        cxt.error(true);
        if (!it.allErrors) gen.break();
      });
    });
    cxt.ok(valid);
  }
};
propertyNames.default = def$b;

var additionalProperties = {};

Object.defineProperty(additionalProperties, "__esModule", {
  value: true
});
const code_1$3 = code;
const codegen_1$5 = codegen;
const names_1 = names$1;
const util_1$8 = util;
const error$5 = {
  message: "must NOT have additional properties",
  params: ({
    params
  }) => (0, codegen_1$5._)`{additionalProperty: ${params.additionalProperty}}`
};
const def$a = {
  keyword: "additionalProperties",
  type: ["object"],
  schemaType: ["boolean", "object"],
  allowUndefined: true,
  trackErrors: true,
  error: error$5,
  code(cxt) {
    const {
      gen,
      schema,
      parentSchema,
      data,
      errsCount,
      it
    } = cxt;
    /* istanbul ignore if */
    if (!errsCount) throw new Error("ajv implementation error");
    const {
      allErrors,
      opts
    } = it;
    it.props = true;
    if (opts.removeAdditional !== "all" && (0, util_1$8.alwaysValidSchema)(it, schema)) return;
    const props = (0, code_1$3.allSchemaProperties)(parentSchema.properties);
    const patProps = (0, code_1$3.allSchemaProperties)(parentSchema.patternProperties);
    checkAdditionalProperties();
    cxt.ok((0, codegen_1$5._)`${errsCount} === ${names_1.default.errors}`);
    function checkAdditionalProperties() {
      gen.forIn("key", data, key => {
        if (!props.length && !patProps.length) additionalPropertyCode(key);else gen.if(isAdditional(key), () => additionalPropertyCode(key));
      });
    }
    function isAdditional(key) {
      let definedProp;
      if (props.length > 8) {
        // TODO maybe an option instead of hard-coded 8?
        const propsSchema = (0, util_1$8.schemaRefOrVal)(it, parentSchema.properties, "properties");
        definedProp = (0, code_1$3.isOwnProperty)(gen, propsSchema, key);
      } else if (props.length) {
        definedProp = (0, codegen_1$5.or)(...props.map(p => (0, codegen_1$5._)`${key} === ${p}`));
      } else {
        definedProp = codegen_1$5.nil;
      }
      if (patProps.length) {
        definedProp = (0, codegen_1$5.or)(definedProp, ...patProps.map(p => (0, codegen_1$5._)`${(0, code_1$3.usePattern)(cxt, p)}.test(${key})`));
      }
      return (0, codegen_1$5.not)(definedProp);
    }
    function deleteAdditional(key) {
      gen.code((0, codegen_1$5._)`delete ${data}[${key}]`);
    }
    function additionalPropertyCode(key) {
      if (opts.removeAdditional === "all" || opts.removeAdditional && schema === false) {
        deleteAdditional(key);
        return;
      }
      if (schema === false) {
        cxt.setParams({
          additionalProperty: key
        });
        cxt.error();
        if (!allErrors) gen.break();
        return;
      }
      if (typeof schema == "object" && !(0, util_1$8.alwaysValidSchema)(it, schema)) {
        const valid = gen.name("valid");
        if (opts.removeAdditional === "failing") {
          applyAdditionalSchema(key, valid, false);
          gen.if((0, codegen_1$5.not)(valid), () => {
            cxt.reset();
            deleteAdditional(key);
          });
        } else {
          applyAdditionalSchema(key, valid);
          if (!allErrors) gen.if((0, codegen_1$5.not)(valid), () => gen.break());
        }
      }
    }
    function applyAdditionalSchema(key, valid, errors) {
      const subschema = {
        keyword: "additionalProperties",
        dataProp: key,
        dataPropType: util_1$8.Type.Str
      };
      if (errors === false) {
        Object.assign(subschema, {
          compositeRule: true,
          createErrors: false,
          allErrors: false
        });
      }
      cxt.subschema(subschema, valid);
    }
  }
};
additionalProperties.default = def$a;

var properties$1 = {};

Object.defineProperty(properties$1, "__esModule", {
  value: true
});
const validate_1 = validate;
const code_1$2 = code;
const util_1$7 = util;
const additionalProperties_1$1 = additionalProperties;
const def$9 = {
  keyword: "properties",
  type: "object",
  schemaType: "object",
  code(cxt) {
    const {
      gen,
      schema,
      parentSchema,
      data,
      it
    } = cxt;
    if (it.opts.removeAdditional === "all" && parentSchema.additionalProperties === undefined) {
      additionalProperties_1$1.default.code(new validate_1.KeywordCxt(it, additionalProperties_1$1.default, "additionalProperties"));
    }
    const allProps = (0, code_1$2.allSchemaProperties)(schema);
    for (const prop of allProps) {
      it.definedProperties.add(prop);
    }
    if (it.opts.unevaluated && allProps.length && it.props !== true) {
      it.props = util_1$7.mergeEvaluated.props(gen, (0, util_1$7.toHash)(allProps), it.props);
    }
    const properties = allProps.filter(p => !(0, util_1$7.alwaysValidSchema)(it, schema[p]));
    if (properties.length === 0) return;
    const valid = gen.name("valid");
    for (const prop of properties) {
      if (hasDefault(prop)) {
        applyPropertySchema(prop);
      } else {
        gen.if((0, code_1$2.propertyInData)(gen, data, prop, it.opts.ownProperties));
        applyPropertySchema(prop);
        if (!it.allErrors) gen.else().var(valid, true);
        gen.endIf();
      }
      cxt.it.definedProperties.add(prop);
      cxt.ok(valid);
    }
    function hasDefault(prop) {
      return it.opts.useDefaults && !it.compositeRule && schema[prop].default !== undefined;
    }
    function applyPropertySchema(prop) {
      cxt.subschema({
        keyword: "properties",
        schemaProp: prop,
        dataProp: prop
      }, valid);
    }
  }
};
properties$1.default = def$9;

var patternProperties = {};

Object.defineProperty(patternProperties, "__esModule", {
  value: true
});
const code_1$1 = code;
const codegen_1$4 = codegen;
const util_1$6 = util;
const util_2 = util;
const def$8 = {
  keyword: "patternProperties",
  type: "object",
  schemaType: "object",
  code(cxt) {
    const {
      gen,
      schema,
      data,
      parentSchema,
      it
    } = cxt;
    const {
      opts
    } = it;
    const patterns = (0, code_1$1.allSchemaProperties)(schema);
    const alwaysValidPatterns = patterns.filter(p => (0, util_1$6.alwaysValidSchema)(it, schema[p]));
    if (patterns.length === 0 || alwaysValidPatterns.length === patterns.length && (!it.opts.unevaluated || it.props === true)) {
      return;
    }
    const checkProperties = opts.strictSchema && !opts.allowMatchingProperties && parentSchema.properties;
    const valid = gen.name("valid");
    if (it.props !== true && !(it.props instanceof codegen_1$4.Name)) {
      it.props = (0, util_2.evaluatedPropsToName)(gen, it.props);
    }
    const {
      props
    } = it;
    validatePatternProperties();
    function validatePatternProperties() {
      for (const pat of patterns) {
        if (checkProperties) checkMatchingProperties(pat);
        if (it.allErrors) {
          validateProperties(pat);
        } else {
          gen.var(valid, true); // TODO var
          validateProperties(pat);
          gen.if(valid);
        }
      }
    }
    function checkMatchingProperties(pat) {
      for (const prop in checkProperties) {
        if (new RegExp(pat).test(prop)) {
          (0, util_1$6.checkStrictMode)(it, `property ${prop} matches pattern ${pat} (use allowMatchingProperties)`);
        }
      }
    }
    function validateProperties(pat) {
      gen.forIn("key", data, key => {
        gen.if((0, codegen_1$4._)`${(0, code_1$1.usePattern)(cxt, pat)}.test(${key})`, () => {
          const alwaysValid = alwaysValidPatterns.includes(pat);
          if (!alwaysValid) {
            cxt.subschema({
              keyword: "patternProperties",
              schemaProp: pat,
              dataProp: key,
              dataPropType: util_2.Type.Str
            }, valid);
          }
          if (it.opts.unevaluated && props !== true) {
            gen.assign((0, codegen_1$4._)`${props}[${key}]`, true);
          } else if (!alwaysValid && !it.allErrors) {
            // can short-circuit if `unevaluatedProperties` is not supported (opts.next === false)
            // or if all properties were evaluated (props === true)
            gen.if((0, codegen_1$4.not)(valid), () => gen.break());
          }
        });
      });
    }
  }
};
patternProperties.default = def$8;

var not = {};

Object.defineProperty(not, "__esModule", {
  value: true
});
const util_1$5 = util;
const def$7 = {
  keyword: "not",
  schemaType: ["object", "boolean"],
  trackErrors: true,
  code(cxt) {
    const {
      gen,
      schema,
      it
    } = cxt;
    if ((0, util_1$5.alwaysValidSchema)(it, schema)) {
      cxt.fail();
      return;
    }
    const valid = gen.name("valid");
    cxt.subschema({
      keyword: "not",
      compositeRule: true,
      createErrors: false,
      allErrors: false
    }, valid);
    cxt.failResult(valid, () => cxt.reset(), () => cxt.error());
  },
  error: {
    message: "must NOT be valid"
  }
};
not.default = def$7;

var anyOf = {};

Object.defineProperty(anyOf, "__esModule", {
  value: true
});
const code_1 = code;
const def$6 = {
  keyword: "anyOf",
  schemaType: "array",
  trackErrors: true,
  code: code_1.validateUnion,
  error: {
    message: "must match a schema in anyOf"
  }
};
anyOf.default = def$6;

var oneOf = {};

Object.defineProperty(oneOf, "__esModule", {
  value: true
});
const codegen_1$3 = codegen;
const util_1$4 = util;
const error$4 = {
  message: "must match exactly one schema in oneOf",
  params: ({
    params
  }) => (0, codegen_1$3._)`{passingSchemas: ${params.passing}}`
};
const def$5 = {
  keyword: "oneOf",
  schemaType: "array",
  trackErrors: true,
  error: error$4,
  code(cxt) {
    const {
      gen,
      schema,
      parentSchema,
      it
    } = cxt;
    /* istanbul ignore if */
    if (!Array.isArray(schema)) throw new Error("ajv implementation error");
    if (it.opts.discriminator && parentSchema.discriminator) return;
    const schArr = schema;
    const valid = gen.let("valid", false);
    const passing = gen.let("passing", null);
    const schValid = gen.name("_valid");
    cxt.setParams({
      passing
    });
    // TODO possibly fail straight away (with warning or exception) if there are two empty always valid schemas
    gen.block(validateOneOf);
    cxt.result(valid, () => cxt.reset(), () => cxt.error(true));
    function validateOneOf() {
      schArr.forEach((sch, i) => {
        let schCxt;
        if ((0, util_1$4.alwaysValidSchema)(it, sch)) {
          gen.var(schValid, true);
        } else {
          schCxt = cxt.subschema({
            keyword: "oneOf",
            schemaProp: i,
            compositeRule: true
          }, schValid);
        }
        if (i > 0) {
          gen.if((0, codegen_1$3._)`${schValid} && ${valid}`).assign(valid, false).assign(passing, (0, codegen_1$3._)`[${passing}, ${i}]`).else();
        }
        gen.if(schValid, () => {
          gen.assign(valid, true);
          gen.assign(passing, i);
          if (schCxt) cxt.mergeEvaluated(schCxt, codegen_1$3.Name);
        });
      });
    }
  }
};
oneOf.default = def$5;

var allOf = {};

Object.defineProperty(allOf, "__esModule", {
  value: true
});
const util_1$3 = util;
const def$4 = {
  keyword: "allOf",
  schemaType: "array",
  code(cxt) {
    const {
      gen,
      schema,
      it
    } = cxt;
    /* istanbul ignore if */
    if (!Array.isArray(schema)) throw new Error("ajv implementation error");
    const valid = gen.name("valid");
    schema.forEach((sch, i) => {
      if ((0, util_1$3.alwaysValidSchema)(it, sch)) return;
      const schCxt = cxt.subschema({
        keyword: "allOf",
        schemaProp: i
      }, valid);
      cxt.ok(valid);
      cxt.mergeEvaluated(schCxt);
    });
  }
};
allOf.default = def$4;

var _if = {};

Object.defineProperty(_if, "__esModule", {
  value: true
});
const codegen_1$2 = codegen;
const util_1$2 = util;
const error$3 = {
  message: ({
    params
  }) => (0, codegen_1$2.str)`must match "${params.ifClause}" schema`,
  params: ({
    params
  }) => (0, codegen_1$2._)`{failingKeyword: ${params.ifClause}}`
};
const def$3 = {
  keyword: "if",
  schemaType: ["object", "boolean"],
  trackErrors: true,
  error: error$3,
  code(cxt) {
    const {
      gen,
      parentSchema,
      it
    } = cxt;
    if (parentSchema.then === undefined && parentSchema.else === undefined) {
      (0, util_1$2.checkStrictMode)(it, '"if" without "then" and "else" is ignored');
    }
    const hasThen = hasSchema(it, "then");
    const hasElse = hasSchema(it, "else");
    if (!hasThen && !hasElse) return;
    const valid = gen.let("valid", true);
    const schValid = gen.name("_valid");
    validateIf();
    cxt.reset();
    if (hasThen && hasElse) {
      const ifClause = gen.let("ifClause");
      cxt.setParams({
        ifClause
      });
      gen.if(schValid, validateClause("then", ifClause), validateClause("else", ifClause));
    } else if (hasThen) {
      gen.if(schValid, validateClause("then"));
    } else {
      gen.if((0, codegen_1$2.not)(schValid), validateClause("else"));
    }
    cxt.pass(valid, () => cxt.error(true));
    function validateIf() {
      const schCxt = cxt.subschema({
        keyword: "if",
        compositeRule: true,
        createErrors: false,
        allErrors: false
      }, schValid);
      cxt.mergeEvaluated(schCxt);
    }
    function validateClause(keyword, ifClause) {
      return () => {
        const schCxt = cxt.subschema({
          keyword
        }, schValid);
        gen.assign(valid, schValid);
        cxt.mergeValidEvaluated(schCxt, valid);
        if (ifClause) gen.assign(ifClause, (0, codegen_1$2._)`${keyword}`);else cxt.setParams({
          ifClause: keyword
        });
      };
    }
  }
};
function hasSchema(it, keyword) {
  const schema = it.schema[keyword];
  return schema !== undefined && !(0, util_1$2.alwaysValidSchema)(it, schema);
}
_if.default = def$3;

var thenElse = {};

Object.defineProperty(thenElse, "__esModule", {
  value: true
});
const util_1$1 = util;
const def$2 = {
  keyword: ["then", "else"],
  schemaType: ["object", "boolean"],
  code({
    keyword,
    parentSchema,
    it
  }) {
    if (parentSchema.if === undefined) (0, util_1$1.checkStrictMode)(it, `"${keyword}" without "if" is ignored`);
  }
};
thenElse.default = def$2;

Object.defineProperty(applicator, "__esModule", {
  value: true
});
const additionalItems_1 = additionalItems;
const prefixItems_1 = prefixItems;
const items_1 = items;
const items2020_1 = items2020;
const contains_1 = contains;
const dependencies_1 = dependencies;
const propertyNames_1 = propertyNames;
const additionalProperties_1 = additionalProperties;
const properties_1 = properties$1;
const patternProperties_1 = patternProperties;
const not_1 = not;
const anyOf_1 = anyOf;
const oneOf_1 = oneOf;
const allOf_1 = allOf;
const if_1 = _if;
const thenElse_1 = thenElse;
function getApplicator(draft2020 = false) {
  const applicator = [
  // any
  not_1.default, anyOf_1.default, oneOf_1.default, allOf_1.default, if_1.default, thenElse_1.default,
  // object
  propertyNames_1.default, additionalProperties_1.default, dependencies_1.default, properties_1.default, patternProperties_1.default];
  // array
  if (draft2020) applicator.push(prefixItems_1.default, items2020_1.default);else applicator.push(additionalItems_1.default, items_1.default);
  applicator.push(contains_1.default);
  return applicator;
}
applicator.default = getApplicator;

var format$2 = {};

var format$1 = {};

Object.defineProperty(format$1, "__esModule", {
  value: true
});
const codegen_1$1 = codegen;
const error$2 = {
  message: ({
    schemaCode
  }) => (0, codegen_1$1.str)`must match format "${schemaCode}"`,
  params: ({
    schemaCode
  }) => (0, codegen_1$1._)`{format: ${schemaCode}}`
};
const def$1 = {
  keyword: "format",
  type: ["number", "string"],
  schemaType: "string",
  $data: true,
  error: error$2,
  code(cxt, ruleType) {
    const {
      gen,
      data,
      $data,
      schema,
      schemaCode,
      it
    } = cxt;
    const {
      opts,
      errSchemaPath,
      schemaEnv,
      self
    } = it;
    if (!opts.validateFormats) return;
    if ($data) validate$DataFormat();else validateFormat();
    function validate$DataFormat() {
      const fmts = gen.scopeValue("formats", {
        ref: self.formats,
        code: opts.code.formats
      });
      const fDef = gen.const("fDef", (0, codegen_1$1._)`${fmts}[${schemaCode}]`);
      const fType = gen.let("fType");
      const format = gen.let("format");
      // TODO simplify
      gen.if((0, codegen_1$1._)`typeof ${fDef} == "object" && !(${fDef} instanceof RegExp)`, () => gen.assign(fType, (0, codegen_1$1._)`${fDef}.type || "string"`).assign(format, (0, codegen_1$1._)`${fDef}.validate`), () => gen.assign(fType, (0, codegen_1$1._)`"string"`).assign(format, fDef));
      cxt.fail$data((0, codegen_1$1.or)(unknownFmt(), invalidFmt()));
      function unknownFmt() {
        if (opts.strictSchema === false) return codegen_1$1.nil;
        return (0, codegen_1$1._)`${schemaCode} && !${format}`;
      }
      function invalidFmt() {
        const callFormat = schemaEnv.$async ? (0, codegen_1$1._)`(${fDef}.async ? await ${format}(${data}) : ${format}(${data}))` : (0, codegen_1$1._)`${format}(${data})`;
        const validData = (0, codegen_1$1._)`(typeof ${format} == "function" ? ${callFormat} : ${format}.test(${data}))`;
        return (0, codegen_1$1._)`${format} && ${format} !== true && ${fType} === ${ruleType} && !${validData}`;
      }
    }
    function validateFormat() {
      const formatDef = self.formats[schema];
      if (!formatDef) {
        unknownFormat();
        return;
      }
      if (formatDef === true) return;
      const [fmtType, format, fmtRef] = getFormat(formatDef);
      if (fmtType === ruleType) cxt.pass(validCondition());
      function unknownFormat() {
        if (opts.strictSchema === false) {
          self.logger.warn(unknownMsg());
          return;
        }
        throw new Error(unknownMsg());
        function unknownMsg() {
          return `unknown format "${schema}" ignored in schema at path "${errSchemaPath}"`;
        }
      }
      function getFormat(fmtDef) {
        const code = fmtDef instanceof RegExp ? (0, codegen_1$1.regexpCode)(fmtDef) : opts.code.formats ? (0, codegen_1$1._)`${opts.code.formats}${(0, codegen_1$1.getProperty)(schema)}` : undefined;
        const fmt = gen.scopeValue("formats", {
          key: schema,
          ref: fmtDef,
          code
        });
        if (typeof fmtDef == "object" && !(fmtDef instanceof RegExp)) {
          return [fmtDef.type || "string", fmtDef.validate, (0, codegen_1$1._)`${fmt}.validate`];
        }
        return ["string", fmtDef, fmt];
      }
      function validCondition() {
        if (typeof formatDef == "object" && !(formatDef instanceof RegExp) && formatDef.async) {
          if (!schemaEnv.$async) throw new Error("async format in sync schema");
          return (0, codegen_1$1._)`await ${fmtRef}(${data})`;
        }
        return typeof format == "function" ? (0, codegen_1$1._)`${fmtRef}(${data})` : (0, codegen_1$1._)`${fmtRef}.test(${data})`;
      }
    }
  }
};
format$1.default = def$1;

Object.defineProperty(format$2, "__esModule", {
  value: true
});
const format_1$1 = format$1;
const format = [format_1$1.default];
format$2.default = format;

var metadata = {};

Object.defineProperty(metadata, "__esModule", {
  value: true
});
metadata.contentVocabulary = metadata.metadataVocabulary = void 0;
metadata.metadataVocabulary = ["title", "description", "default", "deprecated", "readOnly", "writeOnly", "examples"];
metadata.contentVocabulary = ["contentMediaType", "contentEncoding", "contentSchema"];

Object.defineProperty(draft7, "__esModule", {
  value: true
});
const core_1 = core$1;
const validation_1 = validation$1;
const applicator_1 = applicator;
const format_1 = format$2;
const metadata_1 = metadata;
const draft7Vocabularies = [core_1.default, validation_1.default, (0, applicator_1.default)(), format_1.default, metadata_1.metadataVocabulary, metadata_1.contentVocabulary];
draft7.default = draft7Vocabularies;

var discriminator = {};

var types = {};

Object.defineProperty(types, "__esModule", {
  value: true
});
types.DiscrError = void 0;
var DiscrError;
(function (DiscrError) {
  DiscrError["Tag"] = "tag";
  DiscrError["Mapping"] = "mapping";
})(DiscrError || (types.DiscrError = DiscrError = {}));

Object.defineProperty(discriminator, "__esModule", {
  value: true
});
const codegen_1 = codegen;
const types_1 = types;
const compile_1 = compile;
const ref_error_1 = ref_error;
const util_1 = util;
const error$1 = {
  message: ({
    params: {
      discrError,
      tagName
    }
  }) => discrError === types_1.DiscrError.Tag ? `tag "${tagName}" must be string` : `value of tag "${tagName}" must be in oneOf`,
  params: ({
    params: {
      discrError,
      tag,
      tagName
    }
  }) => (0, codegen_1._)`{error: ${discrError}, tag: ${tagName}, tagValue: ${tag}}`
};
const def = {
  keyword: "discriminator",
  type: "object",
  schemaType: "object",
  error: error$1,
  code(cxt) {
    const {
      gen,
      data,
      schema,
      parentSchema,
      it
    } = cxt;
    const {
      oneOf
    } = parentSchema;
    if (!it.opts.discriminator) {
      throw new Error("discriminator: requires discriminator option");
    }
    const tagName = schema.propertyName;
    if (typeof tagName != "string") throw new Error("discriminator: requires propertyName");
    if (schema.mapping) throw new Error("discriminator: mapping is not supported");
    if (!oneOf) throw new Error("discriminator: requires oneOf keyword");
    const valid = gen.let("valid", false);
    const tag = gen.const("tag", (0, codegen_1._)`${data}${(0, codegen_1.getProperty)(tagName)}`);
    gen.if((0, codegen_1._)`typeof ${tag} == "string"`, () => validateMapping(), () => cxt.error(false, {
      discrError: types_1.DiscrError.Tag,
      tag,
      tagName
    }));
    cxt.ok(valid);
    function validateMapping() {
      const mapping = getMapping();
      gen.if(false);
      for (const tagValue in mapping) {
        gen.elseIf((0, codegen_1._)`${tag} === ${tagValue}`);
        gen.assign(valid, applyTagSchema(mapping[tagValue]));
      }
      gen.else();
      cxt.error(false, {
        discrError: types_1.DiscrError.Mapping,
        tag,
        tagName
      });
      gen.endIf();
    }
    function applyTagSchema(schemaProp) {
      const _valid = gen.name("valid");
      const schCxt = cxt.subschema({
        keyword: "oneOf",
        schemaProp
      }, _valid);
      cxt.mergeEvaluated(schCxt, codegen_1.Name);
      return _valid;
    }
    function getMapping() {
      var _a;
      const oneOfMapping = {};
      const topRequired = hasRequired(parentSchema);
      let tagRequired = true;
      for (let i = 0; i < oneOf.length; i++) {
        let sch = oneOf[i];
        if ((sch === null || sch === void 0 ? void 0 : sch.$ref) && !(0, util_1.schemaHasRulesButRef)(sch, it.self.RULES)) {
          const ref = sch.$ref;
          sch = compile_1.resolveRef.call(it.self, it.schemaEnv.root, it.baseId, ref);
          if (sch instanceof compile_1.SchemaEnv) sch = sch.schema;
          if (sch === undefined) throw new ref_error_1.default(it.opts.uriResolver, it.baseId, ref);
        }
        const propSch = (_a = sch === null || sch === void 0 ? void 0 : sch.properties) === null || _a === void 0 ? void 0 : _a[tagName];
        if (typeof propSch != "object") {
          throw new Error(`discriminator: oneOf subschemas (or referenced schemas) must have "properties/${tagName}"`);
        }
        tagRequired = tagRequired && (topRequired || hasRequired(sch));
        addMappings(propSch, i);
      }
      if (!tagRequired) throw new Error(`discriminator: "${tagName}" must be required`);
      return oneOfMapping;
      function hasRequired({
        required
      }) {
        return Array.isArray(required) && required.includes(tagName);
      }
      function addMappings(sch, i) {
        if (sch.const) {
          addMapping(sch.const, i);
        } else if (sch.enum) {
          for (const tagValue of sch.enum) {
            addMapping(tagValue, i);
          }
        } else {
          throw new Error(`discriminator: "properties/${tagName}" must have "const" or "enum"`);
        }
      }
      function addMapping(tagValue, i) {
        if (typeof tagValue != "string" || tagValue in oneOfMapping) {
          throw new Error(`discriminator: "${tagName}" values must be unique strings`);
        }
        oneOfMapping[tagValue] = i;
      }
    }
  }
};
discriminator.default = def;

const $schema = "http://json-schema.org/draft-07/schema#";
const $id = "http://json-schema.org/draft-07/schema#";
const title = "Core schema meta-schema";
const definitions = {
	schemaArray: {
		type: "array",
		minItems: 1,
		items: {
			$ref: "#"
		}
	},
	nonNegativeInteger: {
		type: "integer",
		minimum: 0
	},
	nonNegativeIntegerDefault0: {
		allOf: [
			{
				$ref: "#/definitions/nonNegativeInteger"
			},
			{
				"default": 0
			}
		]
	},
	simpleTypes: {
		"enum": [
			"array",
			"boolean",
			"integer",
			"null",
			"number",
			"object",
			"string"
		]
	},
	stringArray: {
		type: "array",
		items: {
			type: "string"
		},
		uniqueItems: true,
		"default": [
		]
	}
};
const type = [
	"object",
	"boolean"
];
const properties = {
	$id: {
		type: "string",
		format: "uri-reference"
	},
	$schema: {
		type: "string",
		format: "uri"
	},
	$ref: {
		type: "string",
		format: "uri-reference"
	},
	$comment: {
		type: "string"
	},
	title: {
		type: "string"
	},
	description: {
		type: "string"
	},
	"default": true,
	readOnly: {
		type: "boolean",
		"default": false
	},
	examples: {
		type: "array",
		items: true
	},
	multipleOf: {
		type: "number",
		exclusiveMinimum: 0
	},
	maximum: {
		type: "number"
	},
	exclusiveMaximum: {
		type: "number"
	},
	minimum: {
		type: "number"
	},
	exclusiveMinimum: {
		type: "number"
	},
	maxLength: {
		$ref: "#/definitions/nonNegativeInteger"
	},
	minLength: {
		$ref: "#/definitions/nonNegativeIntegerDefault0"
	},
	pattern: {
		type: "string",
		format: "regex"
	},
	additionalItems: {
		$ref: "#"
	},
	items: {
		anyOf: [
			{
				$ref: "#"
			},
			{
				$ref: "#/definitions/schemaArray"
			}
		],
		"default": true
	},
	maxItems: {
		$ref: "#/definitions/nonNegativeInteger"
	},
	minItems: {
		$ref: "#/definitions/nonNegativeIntegerDefault0"
	},
	uniqueItems: {
		type: "boolean",
		"default": false
	},
	contains: {
		$ref: "#"
	},
	maxProperties: {
		$ref: "#/definitions/nonNegativeInteger"
	},
	minProperties: {
		$ref: "#/definitions/nonNegativeIntegerDefault0"
	},
	required: {
		$ref: "#/definitions/stringArray"
	},
	additionalProperties: {
		$ref: "#"
	},
	definitions: {
		type: "object",
		additionalProperties: {
			$ref: "#"
		},
		"default": {
		}
	},
	properties: {
		type: "object",
		additionalProperties: {
			$ref: "#"
		},
		"default": {
		}
	},
	patternProperties: {
		type: "object",
		additionalProperties: {
			$ref: "#"
		},
		propertyNames: {
			format: "regex"
		},
		"default": {
		}
	},
	dependencies: {
		type: "object",
		additionalProperties: {
			anyOf: [
				{
					$ref: "#"
				},
				{
					$ref: "#/definitions/stringArray"
				}
			]
		}
	},
	propertyNames: {
		$ref: "#"
	},
	"const": true,
	"enum": {
		type: "array",
		items: true,
		minItems: 1,
		uniqueItems: true
	},
	type: {
		anyOf: [
			{
				$ref: "#/definitions/simpleTypes"
			},
			{
				type: "array",
				items: {
					$ref: "#/definitions/simpleTypes"
				},
				minItems: 1,
				uniqueItems: true
			}
		]
	},
	format: {
		type: "string"
	},
	contentMediaType: {
		type: "string"
	},
	contentEncoding: {
		type: "string"
	},
	"if": {
		$ref: "#"
	},
	then: {
		$ref: "#"
	},
	"else": {
		$ref: "#"
	},
	allOf: {
		$ref: "#/definitions/schemaArray"
	},
	anyOf: {
		$ref: "#/definitions/schemaArray"
	},
	oneOf: {
		$ref: "#/definitions/schemaArray"
	},
	not: {
		$ref: "#"
	}
};
const require$$3 = {
	$schema: $schema,
	$id: $id,
	title: title,
	definitions: definitions,
	type: type,
	properties: properties,
	"default": true
};

(function (module, exports) {

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.MissingRefError = exports.ValidationError = exports.CodeGen = exports.Name = exports.nil = exports.stringify = exports.str = exports._ = exports.KeywordCxt = exports.Ajv = void 0;
	const core_1 = core$2;
	const draft7_1 = draft7;
	const discriminator_1 = discriminator;
	const draft7MetaSchema = require$$3;
	const META_SUPPORT_DATA = ["/properties"];
	const META_SCHEMA_ID = "http://json-schema.org/draft-07/schema";
	class Ajv extends core_1.default {
	  _addVocabularies() {
	    super._addVocabularies();
	    draft7_1.default.forEach(v => this.addVocabulary(v));
	    if (this.opts.discriminator) this.addKeyword(discriminator_1.default);
	  }
	  _addDefaultMetaSchema() {
	    super._addDefaultMetaSchema();
	    if (!this.opts.meta) return;
	    const metaSchema = this.opts.$data ? this.$dataMetaSchema(draft7MetaSchema, META_SUPPORT_DATA) : draft7MetaSchema;
	    this.addMetaSchema(metaSchema, META_SCHEMA_ID, false);
	    this.refs["http://json-schema.org/schema"] = META_SCHEMA_ID;
	  }
	  defaultMeta() {
	    return this.opts.defaultMeta = super.defaultMeta() || (this.getSchema(META_SCHEMA_ID) ? META_SCHEMA_ID : undefined);
	  }
	}
	exports.Ajv = Ajv;
	module.exports = exports = Ajv;
	module.exports.Ajv = Ajv;
	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	exports.default = Ajv;
	var validate_1 = validate;
	Object.defineProperty(exports, "KeywordCxt", {
	  enumerable: true,
	  get: function () {
	    return validate_1.KeywordCxt;
	  }
	});
	var codegen_1 = codegen;
	Object.defineProperty(exports, "_", {
	  enumerable: true,
	  get: function () {
	    return codegen_1._;
	  }
	});
	Object.defineProperty(exports, "str", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.str;
	  }
	});
	Object.defineProperty(exports, "stringify", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.stringify;
	  }
	});
	Object.defineProperty(exports, "nil", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.nil;
	  }
	});
	Object.defineProperty(exports, "Name", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.Name;
	  }
	});
	Object.defineProperty(exports, "CodeGen", {
	  enumerable: true,
	  get: function () {
	    return codegen_1.CodeGen;
	  }
	});
	var validation_error_1 = validation_error;
	Object.defineProperty(exports, "ValidationError", {
	  enumerable: true,
	  get: function () {
	    return validation_error_1.default;
	  }
	});
	var ref_error_1 = ref_error;
	Object.defineProperty(exports, "MissingRefError", {
	  enumerable: true,
	  get: function () {
	    return ref_error_1.default;
	  }
	}); 
} (ajv, ajv.exports));

var ajvExports = ajv.exports;
const Ajv = /*@__PURE__*/getDefaultExportFromCjs(ajvExports);

function _defineProperty$1r(e, r, t) {
  return (r = _toPropertyKey$1r(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1r(t) {
  var i = _toPrimitive$1r(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1r(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class BaseAction {
  constructor() {
    _defineProperty$1r(this, "actionName", void 0);
    _defineProperty$1r(this, "validate", void 0);
    _defineProperty$1r(this, "PayloadSchema", void 0);
  }
  async check(payload) {
    if (this.PayloadSchema) {
      this.validate = new Ajv({
        allowUnionTypes: true
      }).compile(this.PayloadSchema);
    }
    if (this.validate && !this.validate(payload)) {
      const errors = this.validate.errors;
      const errorMessages = errors.map((e) => {
        return `Key: ${e.instancePath.split("/").slice(1).join(".")}, Message: ${e.message}`;
      });
      return {
        valid: false,
        message: errorMessages.join("\n") || "未知错误"
      };
    }
    return {
      valid: true
    };
  }
  async handle(payload) {
    const result = await this.check(payload);
    if (!result.valid) {
      return OB11Response.error(result.message, 400);
    }
    try {
      const resData = await this._handle(payload);
      return OB11Response.ok(resData);
    } catch (e) {
      logError("发生错误", e);
      return OB11Response.error(e?.toString() || e?.stack?.toString() || "未知错误，可能操作超时", 200);
    }
  }
  async websocketHandle(payload, echo) {
    const result = await this.check(payload);
    if (!result.valid) {
      return OB11Response.error(result.message, 1400);
    }
    try {
      const resData = await this._handle(payload);
      return OB11Response.ok(resData, echo);
    } catch (e) {
      logError("发生错误", e);
      return OB11Response.error(e.stack?.toString() || e.toString(), 1200, echo);
    }
  }
  async _handle(payload) {
    throw `pleas override ${this.actionName} _handle`;
  }
}

let ActionName = /* @__PURE__ */ function(ActionName2) {
  ActionName2["SharePeer"] = "ArkSharePeer";
  ActionName2["ShareGroupEx"] = "ArkShareGroupEx";
  ActionName2["RebootNormal"] = "reboot_normal";
  ActionName2["GetRobotUinRange"] = "get_robot_uin_range";
  ActionName2["SetOnlineStatus"] = "set_online_status";
  ActionName2["GetFriendsWithCategory"] = "get_friends_with_category";
  ActionName2["GetGroupIgnoreAddRequest"] = "get_group_ignore_add_request";
  ActionName2["SetQQAvatar"] = "set_qq_avatar";
  ActionName2["GetConfig"] = "get_config";
  ActionName2["SetConfig"] = "set_config";
  ActionName2["Debug"] = "debug";
  ActionName2["GetFile"] = "get_file";
  ActionName2["ForwardFriendSingleMsg"] = "forward_friend_single_msg";
  ActionName2["ForwardGroupSingleMsg"] = "forward_group_single_msg";
  ActionName2["TranslateEnWordToZn"] = "translate_en2zh";
  ActionName2["GetGroupFileCount"] = "get_group_file_count";
  ActionName2["GetGroupFileList"] = "get_group_file_list";
  ActionName2["SetGroupFileFolder"] = "set_group_file_folder";
  ActionName2["DelGroupFile"] = "del_group_file";
  ActionName2["DelGroupFileFolder"] = "del_group_file_folder";
  ActionName2["Reboot"] = "set_restart";
  ActionName2["SendLike"] = "send_like";
  ActionName2["GetLoginInfo"] = "get_login_info";
  ActionName2["GetFriendList"] = "get_friend_list";
  ActionName2["GetGroupInfo"] = "get_group_info";
  ActionName2["GetGroupList"] = "get_group_list";
  ActionName2["GetGroupMemberInfo"] = "get_group_member_info";
  ActionName2["GetGroupMemberList"] = "get_group_member_list";
  ActionName2["GetMsg"] = "get_msg";
  ActionName2["SendMsg"] = "send_msg";
  ActionName2["SendGroupMsg"] = "send_group_msg";
  ActionName2["SendPrivateMsg"] = "send_private_msg";
  ActionName2["DeleteMsg"] = "delete_msg";
  ActionName2["SetMsgEmojiLike"] = "set_msg_emoji_like";
  ActionName2["SetGroupAddRequest"] = "set_group_add_request";
  ActionName2["SetFriendAddRequest"] = "set_friend_add_request";
  ActionName2["SetGroupLeave"] = "set_group_leave";
  ActionName2["GetVersionInfo"] = "get_version_info";
  ActionName2["GetStatus"] = "get_status";
  ActionName2["CanSendRecord"] = "can_send_record";
  ActionName2["CanSendImage"] = "can_send_image";
  ActionName2["SetGroupKick"] = "set_group_kick";
  ActionName2["SetGroupBan"] = "set_group_ban";
  ActionName2["SetGroupWholeBan"] = "set_group_whole_ban";
  ActionName2["SetGroupAdmin"] = "set_group_admin";
  ActionName2["SetGroupCard"] = "set_group_card";
  ActionName2["SetGroupName"] = "set_group_name";
  ActionName2["GetImage"] = "get_image";
  ActionName2["GetRecord"] = "get_record";
  ActionName2["CleanCache"] = "clean_cache";
  ActionName2["GetCookies"] = "get_cookies";
  ActionName2["GoCQHTTP_HandleQuickAction"] = ".handle_quick_operation";
  ActionName2["GetGroupHonorInfo"] = "get_group_honor_info";
  ActionName2["GoCQHTTP_GetEssenceMsg"] = "get_essence_msg_list";
  ActionName2["GoCQHTTP_SendGroupNotice"] = "_send_group_notice";
  ActionName2["GoCQHTTP_GetGroupNotice"] = "_get_group_notice";
  ActionName2["GoCQHTTP_SendForwardMsg"] = "send_forward_msg";
  ActionName2["GoCQHTTP_SendGroupForwardMsg"] = "send_group_forward_msg";
  ActionName2["GoCQHTTP_SendPrivateForwardMsg"] = "send_private_forward_msg";
  ActionName2["GoCQHTTP_GetStrangerInfo"] = "get_stranger_info";
  ActionName2["GoCQHTTP_MarkMsgAsRead"] = "mark_msg_as_read";
  ActionName2["GetGuildList"] = "get_guild_list";
  ActionName2["MarkPrivateMsgAsRead"] = "mark_private_msg_as_read";
  ActionName2["MarkGroupMsgAsRead"] = "mark_group_msg_as_read";
  ActionName2["GoCQHTTP_UploadGroupFile"] = "upload_group_file";
  ActionName2["GoCQHTTP_DownloadFile"] = "download_file";
  ActionName2["GoCQHTTP_GetGroupMsgHistory"] = "get_group_msg_history";
  ActionName2["GoCQHTTP_GetForwardMsg"] = "get_forward_msg";
  ActionName2["GetFriendMsgHistory"] = "get_friend_msg_history";
  ActionName2["GetGroupSystemMsg"] = "get_group_system_msg";
  ActionName2["GetOnlineClient"] = "get_online_clients";
  ActionName2["OCRImage"] = "ocr_image";
  ActionName2["IOCRImage"] = ".ocr_image";
  ActionName2["SetSelfProfile"] = "set_self_profile";
  ActionName2["CreateCollection"] = "create_collection";
  ActionName2["GetCollectionList"] = "get_collection_list";
  ActionName2["SetLongNick"] = "set_self_longnick";
  ActionName2["SetEssenceMsg"] = "set_essence_msg";
  ActionName2["DelEssenceMsg"] = "delete_essence_msg";
  ActionName2["GetRecentContact"] = "get_recent_contact";
  ActionName2["_MarkAllMsgAsRead"] = "_mark_all_as_read";
  ActionName2["GetProfileLike"] = "get_profile_like";
  ActionName2["SetGroupHeader"] = "set_group_head";
  ActionName2["FetchCustomFace"] = "fetch_custom_face";
  ActionName2["GOCQHTTP_UploadPrivateFile"] = "upload_private_file";
  ActionName2["TestApi01"] = "test_api_01";
  ActionName2["FetchEmojioLike"] = "fetch_emoji_like";
  return ActionName2;
}({});

console.log(process.pid);
async function handleOb11FileLikeMessage({
  data: inputdata
}, {
  deleteAfterSentFiles
}) {
  const {
    path,
    isLocal,
    fileName,
    errMsg,
    success
  } = await uri2local(inputdata?.url || inputdata.file);
  if (!success) {
    logError("文件下载失败", errMsg);
    throw Error("文件下载失败" + errMsg);
  }
  if (!isLocal) {
    deleteAfterSentFiles.push(path);
  }
  return {
    path,
    fileName: inputdata.name || fileName
  };
}
const _handlers = {
  [OB11MessageDataType.text]: async ({
    data: {
      text
    }
  }) => SendMsgElementConstructor.text(text),
  [OB11MessageDataType.at]: async ({
    data: {
      qq: atQQ
    }
  }, context) => {
    if (!context.peer) return void 0;
    if (atQQ === "all") return SendMsgElementConstructor.at(atQQ, atQQ, AtType.atAll, "全体成员");
    const atMember = await getGroupMember(context.peer.peerUid, atQQ);
    return atMember ? SendMsgElementConstructor.at(atQQ, atMember.uid, AtType.atUser, atMember.cardName || atMember.nick) : void 0;
  },
  [OB11MessageDataType.reply]: async ({
    data: {
      id
    }
  }) => {
    const replyMsgM = MessageUnique.getMsgIdAndPeerByShortId(parseInt(id));
    if (!replyMsgM) {
      logWarn("回复消息不存在", id);
      return void 0;
    }
    const replyMsg = (await NTQQMsgApi.getMsgsByMsgId(replyMsgM?.Peer, [replyMsgM?.MsgId])).msgList[0];
    return replyMsg ? SendMsgElementConstructor.reply(replyMsg.msgSeq, replyMsg.msgId, replyMsg.senderUin, replyMsg.senderUin) : void 0;
  },
  [OB11MessageDataType.face]: async ({
    data: {
      id
    }
  }) => SendMsgElementConstructor.face(parseInt(id)),
  [OB11MessageDataType.mface]: async ({
    data: {
      emoji_package_id,
      emoji_id,
      key,
      summary
    }
  }) => SendMsgElementConstructor.mface(emoji_package_id, emoji_id, key, summary),
  // File service
  [OB11MessageDataType.image]: async (sendMsg, context) => {
    const PicEle = await SendMsgElementConstructor.pic((await handleOb11FileLikeMessage(sendMsg, context)).path, sendMsg.data.summary || "", sendMsg.data.subType || 0);
    context.deleteAfterSentFiles.push(PicEle.picElement.sourcePath);
    return PicEle;
  },
  // currently not supported
  [OB11MessageDataType.file]: async (sendMsg, context) => {
    const {
      path,
      fileName
    } = await handleOb11FileLikeMessage(sendMsg, context);
    const FileEle = await SendMsgElementConstructor.file(path, fileName);
    return FileEle;
  },
  [OB11MessageDataType.video]: async (sendMsg, context) => {
    const {
      path,
      fileName
    } = await handleOb11FileLikeMessage(sendMsg, context);
    let thumb = sendMsg.data.thumb;
    if (thumb) {
      const uri2LocalRes = await uri2local(thumb);
      if (uri2LocalRes.success) thumb = uri2LocalRes.path;
    }
    const videoEle = await SendMsgElementConstructor.video(path, fileName, thumb);
    context.deleteAfterSentFiles.push(videoEle.videoElement.filePath);
    return videoEle;
  },
  [OB11MessageDataType.miniapp]: async ({
    data: any
  }) => SendMsgElementConstructor.miniapp(),
  [OB11MessageDataType.voice]: async (sendMsg, context) => SendMsgElementConstructor.ptt((await handleOb11FileLikeMessage(sendMsg, context)).path),
  [OB11MessageDataType.json]: async ({
    data: {
      data
    }
  }) => SendMsgElementConstructor.ark(data),
  [OB11MessageDataType.dice]: async ({
    data: {
      result
    }
  }) => SendMsgElementConstructor.dice(result),
  [OB11MessageDataType.RPS]: async ({
    data: {
      result
    }
  }) => SendMsgElementConstructor.rps(result),
  [OB11MessageDataType.markdown]: async ({
    data: {
      content
    }
  }) => SendMsgElementConstructor.markdown(content),
  [OB11MessageDataType.music]: async ({
    data
  }) => {
    if (data.type === "custom") {
      if (!data.url) {
        logError("自定义音卡缺少参数url");
        return void 0;
      }
      if (!data.audio) {
        logError("自定义音卡缺少参数audio");
        return void 0;
      }
      if (!data.title) {
        logError("自定义音卡缺少参数title");
        return void 0;
      }
    } else {
      if (!["qq", "163"].includes(data.type)) {
        logError("音乐卡片type错误, 只支持qq、163、custom，当前type:", data.type);
        return void 0;
      }
      if (!data.id) {
        logError("音乐卡片缺少参数id");
        return void 0;
      }
    }
    let postData;
    if (data.type === "custom" && data.content) {
      const {
        content,
        ...others
      } = data;
      postData = {
        singer: content,
        ...others
      };
    } else {
      postData = data;
    }
    const signUrl = ob11Config.musicSignUrl;
    if (!signUrl) {
      if (data.type === "qq") {
        const musicJson = (await SignMusicWrapper(data.id.toString())).data.arkResult.slice(0, -1);
        return SendMsgElementConstructor.ark(musicJson);
      }
      throw Error("音乐消息签名地址未配置");
    }
    try {
      const musicJson = await RequestUtil.HttpGetJson(signUrl, "POST", postData);
      return SendMsgElementConstructor.ark(musicJson);
    } catch (e) {
      logError("生成音乐消息失败", e);
    }
  },
  [OB11MessageDataType.node]: async () => void 0,
  [OB11MessageDataType.forward]: async () => void 0,
  [OB11MessageDataType.xml]: async () => void 0,
  [OB11MessageDataType.poke]: async () => void 0,
  [OB11MessageDataType.Location]: async () => {
    return SendMsgElementConstructor.location();
  }
};
const handlers = _handlers;
async function createSendElements(messageData, peer, ignoreTypes = []) {
  const deleteAfterSentFiles = [];
  const callResultList = [];
  for (const sendMsg of messageData) {
    if (ignoreTypes.includes(sendMsg.type)) {
      continue;
    }
    const callResult = handlers[sendMsg.type](sendMsg, {
      peer,
      deleteAfterSentFiles
    })?.catch(void 0);
    callResultList.push(callResult);
  }
  const ret = await Promise.all(callResultList);
  const sendElements = ret.filter((ele) => ele);
  return {
    sendElements,
    deleteAfterSentFiles
  };
}

async function cloneMsg(msg) {
  const selfPeer = {
    chatType: ChatType.friend,
    peerUid: selfInfo.uid
  };
  const sendElements = [];
  for (const element of msg.elements) {
    sendElements.push(element);
  }
  if (sendElements.length === 0) {
    logDebug("需要clone的消息无法解析，将会忽略掉", msg);
  }
  try {
    const nodeMsg = await NTQQMsgApi.sendMsg(selfPeer, sendElements, true);
    return nodeMsg;
  } catch (e) {
    logError(e, "克隆转发消息失败,将忽略本条消息", msg);
  }
}
async function handleForwardNode(destPeer, messageNodes) {
  const selfPeer = {
    chatType: ChatType.friend,
    peerUid: selfInfo.uid
  };
  let nodeMsgIds = [];
  for (const messageNode of messageNodes) {
    const nodeId = messageNode.data.id;
    if (nodeId) {
      const nodeMsg = MessageUnique.getMsgIdAndPeerByShortId(parseInt(nodeId)) || MessageUnique.getPeerByMsgId(nodeId);
      if (!nodeMsg) {
        logError("转发消息失败，未找到消息", nodeId);
        continue;
      }
      nodeMsgIds.push(nodeMsg.MsgId);
    } else {
      try {
        const OB11Data = normalize(messageNode.data.content);
        const isNodeMsg = OB11Data.filter((e) => e.type === OB11MessageDataType.node).length;
        if (isNodeMsg !== 0) {
          if (isNodeMsg !== OB11Data.length) {
            logError("子消息中包含非node消息 跳过不合法部分");
            continue;
          }
          const nodeMsg = await handleForwardNode(selfPeer, OB11Data.filter((e) => e.type === OB11MessageDataType.node));
          if (nodeMsg) {
            nodeMsgIds.push(nodeMsg.msgId);
            MessageUnique.createMsg(selfPeer, nodeMsg.msgId);
          }
          continue;
        }
        const {
          sendElements
        } = await createSendElements(OB11Data, destPeer);
        const MixElement = sendElements.filter((element) => element.elementType !== ElementType.FILE && element.elementType !== ElementType.VIDEO);
        const SingleElement = sendElements.filter((element) => element.elementType === ElementType.FILE || element.elementType === ElementType.VIDEO).map((e) => [e]);
        const AllElement = [MixElement, ...SingleElement].filter((e) => e !== void 0 && e.length !== 0);
        const MsgNodeList = [];
        for (const sendElementsSplitElement of AllElement) {
          MsgNodeList.push(sendMsg(selfPeer, sendElementsSplitElement, [], true).catch((e) => new Promise((resolve, reject) => {
            resolve(void 0);
          })));
        }
        (await Promise.allSettled(MsgNodeList)).map((result) => {
          if (result.status === "fulfilled" && result.value) {
            nodeMsgIds.push(result.value.msgId);
            MessageUnique.createMsg(selfPeer, result.value.msgId);
          }
        });
      } catch (e) {
        logDebug("生成转发消息节点失败", e);
      }
    }
  }
  const nodeMsgArray = [];
  let srcPeer = void 0;
  let needSendSelf = false;
  for (const msgId of nodeMsgIds) {
    const nodeMsgPeer = MessageUnique.getPeerByMsgId(msgId);
    if (!nodeMsgPeer) {
      logError("转发消息失败，未找到消息", msgId);
      continue;
    }
    const nodeMsg = (await NTQQMsgApi.getMsgsByMsgId(nodeMsgPeer.Peer, [msgId])).msgList[0];
    srcPeer = srcPeer ?? {
      chatType: nodeMsg.chatType,
      peerUid: nodeMsg.peerUid
    };
    if (srcPeer.peerUid !== nodeMsg.peerUid) {
      needSendSelf = true;
    }
    nodeMsgArray.push(nodeMsg);
  }
  nodeMsgIds = nodeMsgArray.map((msg) => msg.msgId);
  let retMsgIds = [];
  if (needSendSelf) {
    for (const [index, msg] of nodeMsgArray.entries()) {
      if (msg.peerUid === selfInfo.uid) continue;
      const ClonedMsg = await cloneMsg(msg);
      if (ClonedMsg) retMsgIds.push(ClonedMsg.msgId);
    }
  } else {
    retMsgIds = nodeMsgIds;
  }
  if (nodeMsgIds.length === 0) throw Error("转发消息失败，生成节点为空");
  try {
    logDebug("开发转发", srcPeer, destPeer, nodeMsgIds);
    return await NTQQMsgApi.multiForwardMsg(srcPeer, destPeer, nodeMsgIds);
  } catch (e) {
    logError("forward failed", e);
    return null;
  }
}

function _defineProperty$1q(e, r, t) {
  return (r = _toPropertyKey$1q(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1q(t) {
  var i = _toPrimitive$1q(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1q(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
let ContextMode = /* @__PURE__ */ function(ContextMode2) {
  ContextMode2[ContextMode2["Normal"] = 0] = "Normal";
  ContextMode2[ContextMode2["Private"] = 1] = "Private";
  ContextMode2[ContextMode2["Group"] = 2] = "Group";
  return ContextMode2;
}({});
function normalize(message, autoEscape = false) {
  return typeof message === "string" ? autoEscape ? [{
    type: OB11MessageDataType.text,
    data: {
      text: message
    }
  }] : decodeCQCode(message) : Array.isArray(message) ? message : [message];
}
async function sendMsg(peer, sendElements, deleteAfterSentFiles, waitComplete = true) {
  if (!sendElements.length) {
    throw "消息体无法解析, 请检查是否发送了不支持的消息类型";
  }
  let totalSize = 0;
  let timeout = 1e4;
  try {
    for (const fileElement of sendElements) {
      if (fileElement.elementType === ElementType.PTT) {
        totalSize += fs__default.statSync(fileElement.pttElement.filePath).size;
      }
      if (fileElement.elementType === ElementType.FILE) {
        totalSize += fs__default.statSync(fileElement.fileElement.filePath).size;
      }
      if (fileElement.elementType === ElementType.VIDEO) {
        totalSize += fs__default.statSync(fileElement.videoElement.filePath).size;
      }
      if (fileElement.elementType === ElementType.PIC) {
        totalSize += fs__default.statSync(fileElement.picElement.sourcePath).size;
      }
    }
    const PredictTime = totalSize / 1024 / 256 * 1e3;
    if (!Number.isNaN(PredictTime)) {
      timeout += PredictTime;
    }
  } catch (e) {
    logError("发送消息计算预计时间异常", e);
  }
  const returnMsg = await NTQQMsgApi.sendMsg(peer, sendElements, waitComplete, timeout);
  try {
    returnMsg.id = MessageUnique.createMsg({
      chatType: peer.chatType,
      guildId: "",
      peerUid: peer.peerUid
    }, returnMsg.msgId);
  } catch (e) {
    logDebug("发送消息id获取失败", e);
    returnMsg.id = 0;
  }
  deleteAfterSentFiles.map((f) => {
    fsPromise$1.unlink(f).then().catch((e) => logError("发送消息删除文件失败", e));
  });
  return returnMsg;
}
async function createContext(payload, contextMode) {
  if ((contextMode === ContextMode.Group || contextMode === ContextMode.Normal) && payload.group_id) {
    const group = await getGroup(payload.group_id);
    return {
      chatType: ChatType.group,
      peerUid: group.groupCode
    };
  }
  if ((contextMode === ContextMode.Private || contextMode === ContextMode.Normal) && payload.user_id) {
    const Uid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
    const isBuddy = await NTQQFriendApi.isBuddy(Uid);
    return {
      chatType: isBuddy ? ChatType.friend : ChatType.temp,
      peerUid: Uid,
      guildId: payload.group_id || ""
      //临时主动发起时需要传入群号
    };
  }
  throw "请指定 group_id 或 user_id";
}
function getSpecialMsgNum(payload, msgType) {
  if (Array.isArray(payload.message)) {
    return payload.message.filter((msg) => msg.type == msgType).length;
  }
  return 0;
}
class SendMsg extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1q(this, "actionName", ActionName.SendMsg);
    _defineProperty$1q(this, "contextMode", ContextMode.Normal);
  }
  async check(payload) {
    const messages = normalize(payload.message);
    const nodeElementLength = getSpecialMsgNum(payload, OB11MessageDataType.node);
    if (nodeElementLength > 0 && nodeElementLength != messages.length) {
      return {
        valid: false,
        message: "转发消息不能和普通消息混在一起发送,转发需要保证message只有type为node的元素"
      };
    }
    if (payload.message_type !== "private" && payload.group_id && !await getGroup(payload.group_id)) {
      return {
        valid: false,
        message: `群${payload.group_id}不存在`
      };
    }
    if (payload.user_id && payload.message_type !== "group") {
      const uid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
      await NTQQFriendApi.isBuddy(uid);
    }
    return {
      valid: true
    };
  }
  async _handle(payload) {
    const peer = await createContext(payload, this.contextMode);
    const messages = normalize(payload.message, payload.auto_escape === true || payload.auto_escape === "true");
    if (getSpecialMsgNum(payload, OB11MessageDataType.node)) {
      const returnMsg2 = await handleForwardNode(peer, messages);
      if (returnMsg2) {
        const msgShortId = MessageUnique.createMsg({
          guildId: "",
          peerUid: peer.peerUid,
          chatType: peer.chatType
        }, returnMsg2.msgId);
        return {
          message_id: msgShortId
        };
      } else {
        throw Error("发送转发消息失败");
      }
    }
    const {
      sendElements,
      deleteAfterSentFiles
    } = await createSendElements(messages, peer);
    const returnMsg = await sendMsg(peer, sendElements, deleteAfterSentFiles);
    return {
      message_id: returnMsg.id
    };
  }
}

const eventWSList = [];
function registerWsEventSender(ws) {
  eventWSList.push(ws);
}
function unregisterWsEventSender(ws) {
  const index = eventWSList.indexOf(ws);
  if (index !== -1) {
    eventWSList.splice(index, 1);
  }
}
function postWsEvent(event) {
  for (const ws of eventWSList) {
    new Promise(() => {
      wsReply(ws, event);
    }).then();
  }
}
function postOB11Event(msg, reportSelf = false, postWs = true) {
  const config = ob11Config;
  if (!config.reportSelfMessage && !reportSelf) {
    if (msg.post_type === "message" && msg.user_id.toString() == selfInfo.uin) {
      return;
    }
  }
  if (config.http.enablePost) {
    const msgStr = JSON.stringify(msg);
    const hmac = crypto.createHmac("sha1", ob11Config.http.secret);
    hmac.update(msgStr);
    const sig = hmac.digest("hex");
    const headers = {
      "Content-Type": "application/json",
      "x-self-id": selfInfo.uin
    };
    if (config.http.secret) {
      headers["x-signature"] = "sha1=" + sig;
    }
    for (const host of config.http.postUrls) {
      fetch(host, {
        method: "POST",
        headers,
        body: msgStr
      }).then(async (res) => {
        let resJson;
        try {
          resJson = await res.json();
        } catch (e) {
          logDebug("新消息事件HTTP上报没有返回快速操作，不需要处理");
          return;
        }
        try {
          handleQuickOperation(msg, resJson).then().catch(logError);
        } catch (e) {
          logError("新消息事件HTTP上报返回快速操作失败", e);
        }
      }, (err) => {
        logError(`新消息事件HTTP上报失败: ${host} `, err, msg);
      });
    }
  }
  if (postWs) {
    postWsEvent(msg);
  }
}
async function handleMsg(msg, quickAction) {
  msg = msg;
  const reply = quickAction.reply;
  const peer = {
    chatType: ChatType.friend,
    peerUid: await NTQQUserApi.getUidByUin(msg.user_id.toString())
  };
  if (msg.message_type == "private") {
    if (msg.sub_type === "group") {
      peer.chatType = ChatType.temp;
    }
  } else {
    peer.chatType = ChatType.group;
    peer.peerUid = msg.group_id.toString();
  }
  if (reply) {
    let replyMessage = [];
    if (msg.message_type == "group") {
      await getGroup(msg.group_id.toString());
      replyMessage.push({
        type: "reply",
        data: {
          id: msg.message_id.toString()
        }
      });
      if (quickAction.at_sender) {
        replyMessage.push({
          type: "at",
          data: {
            qq: msg.user_id.toString()
          }
        });
      }
    }
    replyMessage = replyMessage.concat(normalize(reply, quickAction.auto_escape));
    const {
      sendElements,
      deleteAfterSentFiles
    } = await createSendElements(replyMessage, peer);
    sendMsg(peer, sendElements, deleteAfterSentFiles, false).then().catch(logError);
  }
}
async function handleGroupRequest(request, quickAction) {
  if (!isNull(quickAction.approve)) {
    NTQQGroupApi.handleGroupRequest(request.flag, quickAction.approve ? GroupRequestOperateTypes.approve : GroupRequestOperateTypes.reject, quickAction.reason).then().catch(logError);
  }
}
async function handleFriendRequest(request, quickAction) {
  if (!isNull(quickAction.approve)) {
    NTQQFriendApi.handleFriendRequest(request.flag, !!quickAction.approve).then().catch(logError);
  }
}
async function handleQuickOperation(context, quickAction) {
  if (context.post_type === "message") {
    handleMsg(context, quickAction).then().catch(logError);
  }
  if (context.post_type === "request") {
    const friendRequest = context;
    const groupRequest = context;
    if (friendRequest.request_type === "friend") {
      handleFriendRequest(friendRequest, quickAction).then().catch(logError);
    } else if (groupRequest.request_type === "group") {
      handleGroupRequest(groupRequest, quickAction).then().catch(logError);
    }
  }
}

var lib = {exports: {}};

/*
object-assign
(c) Sindre Sorhus
@license MIT
*/

/* eslint-disable no-unused-vars */
var getOwnPropertySymbols = Object.getOwnPropertySymbols;
var hasOwnProperty = Object.prototype.hasOwnProperty;
var propIsEnumerable = Object.prototype.propertyIsEnumerable;
function toObject(val) {
  if (val === null || val === undefined) {
    throw new TypeError('Object.assign cannot be called with null or undefined');
  }
  return Object(val);
}
function shouldUseNative() {
  try {
    if (!Object.assign) {
      return false;
    }

    // Detect buggy property enumeration order in older V8 versions.

    // https://bugs.chromium.org/p/v8/issues/detail?id=4118
    var test1 = new String('abc'); // eslint-disable-line no-new-wrappers
    test1[5] = 'de';
    if (Object.getOwnPropertyNames(test1)[0] === '5') {
      return false;
    }

    // https://bugs.chromium.org/p/v8/issues/detail?id=3056
    var test2 = {};
    for (var i = 0; i < 10; i++) {
      test2['_' + String.fromCharCode(i)] = i;
    }
    var order2 = Object.getOwnPropertyNames(test2).map(function (n) {
      return test2[n];
    });
    if (order2.join('') !== '0123456789') {
      return false;
    }

    // https://bugs.chromium.org/p/v8/issues/detail?id=3056
    var test3 = {};
    'abcdefghijklmnopqrst'.split('').forEach(function (letter) {
      test3[letter] = letter;
    });
    if (Object.keys(Object.assign({}, test3)).join('') !== 'abcdefghijklmnopqrst') {
      return false;
    }
    return true;
  } catch (err) {
    // We don't expect any of the above to throw, but better to be safe.
    return false;
  }
}
var objectAssign = shouldUseNative() ? Object.assign : function (target, source) {
  var from;
  var to = toObject(target);
  var symbols;
  for (var s = 1; s < arguments.length; s++) {
    from = Object(arguments[s]);
    for (var key in from) {
      if (hasOwnProperty.call(from, key)) {
        to[key] = from[key];
      }
    }
    if (getOwnPropertySymbols) {
      symbols = getOwnPropertySymbols(from);
      for (var i = 0; i < symbols.length; i++) {
        if (propIsEnumerable.call(from, symbols[i])) {
          to[symbols[i]] = from[symbols[i]];
        }
      }
    }
  }
  return to;
};

var vary$1 = {exports: {}};

/*!
 * vary
 * Copyright(c) 2014-2017 Douglas Christopher Wilson
 * MIT Licensed
 */

/**
 * Module exports.
 */
vary$1.exports = vary;
vary$1.exports.append = append;

/**
 * RegExp to match field-name in RFC 7230 sec 3.2
 *
 * field-name    = token
 * token         = 1*tchar
 * tchar         = "!" / "#" / "$" / "%" / "&" / "'" / "*"
 *               / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~"
 *               / DIGIT / ALPHA
 *               ; any VCHAR, except delimiters
 */

var FIELD_NAME_REGEXP = /^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$/;

/**
 * Append a field to a vary header.
 *
 * @param {String} header
 * @param {String|Array} field
 * @return {String}
 * @public
 */

function append(header, field) {
  if (typeof header !== 'string') {
    throw new TypeError('header argument is required');
  }
  if (!field) {
    throw new TypeError('field argument is required');
  }

  // get fields array
  var fields = !Array.isArray(field) ? parse(String(field)) : field;

  // assert on invalid field names
  for (var j = 0; j < fields.length; j++) {
    if (!FIELD_NAME_REGEXP.test(fields[j])) {
      throw new TypeError('field argument contains an invalid header name');
    }
  }

  // existing, unspecified vary
  if (header === '*') {
    return header;
  }

  // enumerate current values
  var val = header;
  var vals = parse(header.toLowerCase());

  // unspecified vary
  if (fields.indexOf('*') !== -1 || vals.indexOf('*') !== -1) {
    return '*';
  }
  for (var i = 0; i < fields.length; i++) {
    var fld = fields[i].toLowerCase();

    // append value (case-preserving)
    if (vals.indexOf(fld) === -1) {
      vals.push(fld);
      val = val ? val + ', ' + fields[i] : fields[i];
    }
  }
  return val;
}

/**
 * Parse a vary header into an array.
 *
 * @param {String} header
 * @return {Array}
 * @private
 */

function parse(header) {
  var end = 0;
  var list = [];
  var start = 0;

  // gather tokens
  for (var i = 0, len = header.length; i < len; i++) {
    switch (header.charCodeAt(i)) {
      case 0x20:
        /*   */
        if (start === end) {
          start = end = i + 1;
        }
        break;
      case 0x2c:
        /* , */
        list.push(header.substring(start, end));
        start = end = i + 1;
        break;
      default:
        end = i + 1;
        break;
    }
  }

  // final token
  list.push(header.substring(start, end));
  return list;
}

/**
 * Mark that a request is varied on a header field.
 *
 * @param {Object} res
 * @param {String|Array} field
 * @public
 */

function vary(res, field) {
  if (!res || !res.getHeader || !res.setHeader) {
    // quack quack
    throw new TypeError('res argument is required');
  }

  // get existing header
  var val = res.getHeader('Vary') || '';
  var header = Array.isArray(val) ? val.join(', ') : String(val);

  // set new header
  if (val = append(header, field)) {
    res.setHeader('Vary', val);
  }
}

var varyExports = vary$1.exports;

(function () {

  var assign = objectAssign;
  var vary = varyExports;
  var defaults = {
    origin: '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
    preflightContinue: false,
    optionsSuccessStatus: 204
  };
  function isString(s) {
    return typeof s === 'string' || s instanceof String;
  }
  function isOriginAllowed(origin, allowedOrigin) {
    if (Array.isArray(allowedOrigin)) {
      for (var i = 0; i < allowedOrigin.length; ++i) {
        if (isOriginAllowed(origin, allowedOrigin[i])) {
          return true;
        }
      }
      return false;
    } else if (isString(allowedOrigin)) {
      return origin === allowedOrigin;
    } else if (allowedOrigin instanceof RegExp) {
      return allowedOrigin.test(origin);
    } else {
      return !!allowedOrigin;
    }
  }
  function configureOrigin(options, req) {
    var requestOrigin = req.headers.origin,
      headers = [],
      isAllowed;
    if (!options.origin || options.origin === '*') {
      // allow any origin
      headers.push([{
        key: 'Access-Control-Allow-Origin',
        value: '*'
      }]);
    } else if (isString(options.origin)) {
      // fixed origin
      headers.push([{
        key: 'Access-Control-Allow-Origin',
        value: options.origin
      }]);
      headers.push([{
        key: 'Vary',
        value: 'Origin'
      }]);
    } else {
      isAllowed = isOriginAllowed(requestOrigin, options.origin);
      // reflect origin
      headers.push([{
        key: 'Access-Control-Allow-Origin',
        value: isAllowed ? requestOrigin : false
      }]);
      headers.push([{
        key: 'Vary',
        value: 'Origin'
      }]);
    }
    return headers;
  }
  function configureMethods(options) {
    var methods = options.methods;
    if (methods.join) {
      methods = options.methods.join(','); // .methods is an array, so turn it into a string
    }
    return {
      key: 'Access-Control-Allow-Methods',
      value: methods
    };
  }
  function configureCredentials(options) {
    if (options.credentials === true) {
      return {
        key: 'Access-Control-Allow-Credentials',
        value: 'true'
      };
    }
    return null;
  }
  function configureAllowedHeaders(options, req) {
    var allowedHeaders = options.allowedHeaders || options.headers;
    var headers = [];
    if (!allowedHeaders) {
      allowedHeaders = req.headers['access-control-request-headers']; // .headers wasn't specified, so reflect the request headers
      headers.push([{
        key: 'Vary',
        value: 'Access-Control-Request-Headers'
      }]);
    } else if (allowedHeaders.join) {
      allowedHeaders = allowedHeaders.join(','); // .headers is an array, so turn it into a string
    }
    if (allowedHeaders && allowedHeaders.length) {
      headers.push([{
        key: 'Access-Control-Allow-Headers',
        value: allowedHeaders
      }]);
    }
    return headers;
  }
  function configureExposedHeaders(options) {
    var headers = options.exposedHeaders;
    if (!headers) {
      return null;
    } else if (headers.join) {
      headers = headers.join(','); // .headers is an array, so turn it into a string
    }
    if (headers && headers.length) {
      return {
        key: 'Access-Control-Expose-Headers',
        value: headers
      };
    }
    return null;
  }
  function configureMaxAge(options) {
    var maxAge = (typeof options.maxAge === 'number' || options.maxAge) && options.maxAge.toString();
    if (maxAge && maxAge.length) {
      return {
        key: 'Access-Control-Max-Age',
        value: maxAge
      };
    }
    return null;
  }
  function applyHeaders(headers, res) {
    for (var i = 0, n = headers.length; i < n; i++) {
      var header = headers[i];
      if (header) {
        if (Array.isArray(header)) {
          applyHeaders(header, res);
        } else if (header.key === 'Vary' && header.value) {
          vary(res, header.value);
        } else if (header.value) {
          res.setHeader(header.key, header.value);
        }
      }
    }
  }
  function cors(options, req, res, next) {
    var headers = [],
      method = req.method && req.method.toUpperCase && req.method.toUpperCase();
    if (method === 'OPTIONS') {
      // preflight
      headers.push(configureOrigin(options, req));
      headers.push(configureCredentials(options));
      headers.push(configureMethods(options));
      headers.push(configureAllowedHeaders(options, req));
      headers.push(configureMaxAge(options));
      headers.push(configureExposedHeaders(options));
      applyHeaders(headers, res);
      if (options.preflightContinue) {
        next();
      } else {
        // Safari (and potentially other browsers) need content-length 0,
        //   for 204 or they just hang waiting for a body
        res.statusCode = options.optionsSuccessStatus;
        res.setHeader('Content-Length', '0');
        res.end();
      }
    } else {
      // actual response
      headers.push(configureOrigin(options, req));
      headers.push(configureCredentials(options));
      headers.push(configureExposedHeaders(options));
      applyHeaders(headers, res);
      next();
    }
  }
  function middlewareWrapper(o) {
    // if options are static (either via defaults or custom options passed in), wrap in a function
    var optionsCallback = null;
    if (typeof o === 'function') {
      optionsCallback = o;
    } else {
      optionsCallback = function (req, cb) {
        cb(null, o);
      };
    }
    return function corsMiddleware(req, res, next) {
      optionsCallback(req, function (err, options) {
        if (err) {
          next(err);
        } else {
          var corsOptions = assign({}, defaults, options);
          var originCallback = null;
          if (corsOptions.origin && typeof corsOptions.origin === 'function') {
            originCallback = corsOptions.origin;
          } else if (corsOptions.origin) {
            originCallback = function (origin, cb) {
              cb(null, corsOptions.origin);
            };
          }
          if (originCallback) {
            originCallback(req.headers.origin, function (err2, origin) {
              if (err2 || !origin) {
                next(err2);
              } else {
                corsOptions.origin = origin;
                cors(corsOptions, req, res, next);
              }
            });
          } else {
            next();
          }
        }
      });
    };
  }

  // can pass either an options hash, an options delegate, or nothing
  lib.exports = middlewareWrapper;
})();

var libExports = lib.exports;
const cors = /*@__PURE__*/getDefaultExportFromCjs(libExports);

function _defineProperty$1p(e, r, t) {
  return (r = _toPropertyKey$1p(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1p(t) {
  var i = _toPrimitive$1p(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1p(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class HttpServerBase {
  get server() {
    return this._server;
  }
  set server(value) {
    this._server = value;
  }
  constructor() {
    _defineProperty$1p(this, "name", "NapCatQQ");
    _defineProperty$1p(this, "expressAPP", void 0);
    _defineProperty$1p(this, "_server", null);
    this.expressAPP = express();
    this.expressAPP.use(cors());
    this.expressAPP.use(express.urlencoded({
      extended: true,
      limit: "5000mb"
    }));
    this.expressAPP.use((req, res, next) => {
      req.headers["content-type"] = "application/json";
      const originalJson = express.json({
        limit: "5000mb"
      });
      originalJson(req, res, (err) => {
        if (err) {
          logError("Error parsing JSON:", err);
          return res.status(400).send("Invalid JSON");
        }
        next();
      });
    });
  }
  authorize(req, res, next) {
    const serverToken = ob11Config.token;
    let clientToken = "";
    const authHeader = req.get("authorization");
    if (authHeader) {
      clientToken = authHeader.split("Bearer ").pop() || "";
    } else if (req.query.access_token) {
      if (Array.isArray(req.query.access_token)) {
        clientToken = req.query.access_token[0].toString();
      } else {
        clientToken = req.query.access_token.toString();
      }
    }
    if (serverToken && clientToken != serverToken) {
      return res.status(403).send(JSON.stringify({
        message: "token verify failed!"
      }));
    }
    next();
  }
  start(port, host) {
    try {
      this.expressAPP.get("/", (req, res) => {
        res.send(`${this.name}已启动`);
      });
      this.listen(port, host);
    } catch (e) {
      logError("HTTP服务启动失败", e.toString());
    }
  }
  stop() {
    if (this.server) {
      this.server.close();
      this.server = null;
    }
  }
  restart(port, host) {
    this.stop();
    this.start(port, host);
  }
  registerRouter(method, url, handler) {
    if (!url.startsWith("/")) {
      url = "/" + url;
    }
    if (!this.expressAPP[method]) {
      const err = `${this.name} register router failed，${method} not exist`;
      logError(err);
      throw err;
    }
    this.expressAPP[method](url, this.authorize, async (req, res) => {
      let payload = req.body;
      if (method == "get") {
        payload = req.query;
      } else if (req.query) {
        payload = {
          ...req.query,
          ...req.body
        };
      }
      logDebug("收到http请求", url, payload);
      try {
        res.send(await handler(res, payload));
      } catch (e) {
        this.handleFailed(res, payload, e);
      }
    });
  }
  listen(port, host = "0.0.0.0") {
    host = host || "0.0.0.0";
    try {
      this.server = this.expressAPP.listen(port, host, () => {
        const info = `${this.name} started ${host}:${port}`;
        log(info);
      }).on("error", (err) => {
        logError("HTTP服务启动失败", err.toString());
      });
    } catch (e) {
      logError("HTTP服务启动失败, 请检查监听的ip地址和端口", e.stack.toString());
    }
  }
}

function _defineProperty$1o(e, r, t) {
  return (r = _toPropertyKey$1o(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1o(t) {
  var i = _toPrimitive$1o(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1o(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$K = {
  type: "object",
  properties: {
    message_id: {
      type: ["number", "string"]
    }
  },
  required: ["message_id"]
};
class GetMsg extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1o(this, "actionName", ActionName.GetMsg);
    _defineProperty$1o(this, "PayloadSchema", SchemaData$K);
  }
  async _handle(payload) {
    if (!payload.message_id) {
      throw Error("参数message_id不能为空");
    }
    const MsgShortId = MessageUnique.getShortIdByMsgId(payload.message_id.toString());
    const msgIdWithPeer = MessageUnique.getMsgIdAndPeerByShortId(MsgShortId || parseInt(payload.message_id.toString()));
    if (!msgIdWithPeer) {
      throw "消息不存在";
    }
    const peer = {
      guildId: "",
      peerUid: msgIdWithPeer?.Peer.peerUid,
      chatType: msgIdWithPeer.Peer.chatType
    };
    const msg = await NTQQMsgApi.getMsgsByMsgId(peer, [msgIdWithPeer?.MsgId || payload.message_id.toString()]);
    const retMsg = await OB11Constructor.message(msg.msgList[0]);
    try {
      retMsg.message_id = MessageUnique.createMsg(peer, msg.msgList[0].msgId);
      retMsg.message_seq = retMsg.message_id;
      retMsg.real_id = retMsg.message_id;
    } catch (e) {
    }
    return retMsg;
  }
}

function _defineProperty$1n(e, r, t) {
  return (r = _toPropertyKey$1n(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1n(t) {
  var i = _toPrimitive$1n(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1n(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetLoginInfo extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1n(this, "actionName", ActionName.GetLoginInfo);
  }
  async _handle(payload) {
    return OB11Constructor.selfInfo(selfInfo);
  }
}

function _defineProperty$1m(e, r, t) {
  return (r = _toPropertyKey$1m(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1m(t) {
  var i = _toPrimitive$1m(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1m(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$J = {
  type: "object",
  properties: {
    no_cache: {
      type: ["boolean", "string"]
    }
  }
};
class GetFriendList extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1m(this, "actionName", ActionName.GetFriendList);
    _defineProperty$1m(this, "PayloadSchema", SchemaData$J);
  }
  async _handle(payload) {
    if (requireMinNTQQBuild("26702")) {
      return OB11Constructor.friendsV2(await NTQQFriendApi.getBuddyV2(payload?.no_cache === true || payload?.no_cache === "true"));
    }
    if (friends.size === 0 || payload?.no_cache === true || payload?.no_cache === "true") {
      const _friends = await NTQQFriendApi.getFriends(true);
      if (_friends.length > 0) {
        friends.clear();
        for (const friend of _friends) {
          friends.set(friend.uid, friend);
        }
      }
    }
    return OB11Constructor.friends(Array.from(friends.values()));
  }
}

function _defineProperty$1l(e, r, t) {
  return (r = _toPropertyKey$1l(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1l(t) {
  var i = _toPrimitive$1l(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1l(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$I = {
  type: "object",
  properties: {
    no_cache: {
      type: ["boolean", "string"]
    }
  }
};
class GetGroupList extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1l(this, "actionName", ActionName.GetGroupList);
    _defineProperty$1l(this, "PayloadSchema", SchemaData$I);
  }
  async _handle(payload) {
    const groupList = await NTQQGroupApi.getGroups(payload?.no_cache === true || payload.no_cache === "true");
    return OB11Constructor.groups(groupList);
  }
}

function _defineProperty$1k(e, r, t) {
  return (r = _toPropertyKey$1k(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1k(t) {
  var i = _toPrimitive$1k(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1k(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$H = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    }
  },
  required: ["group_id"]
};
class GetGroupInfo extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1k(this, "actionName", ActionName.GetGroupInfo);
    _defineProperty$1k(this, "PayloadSchema", SchemaData$H);
  }
  async _handle(payload) {
    const group = await getGroup(payload.group_id.toString());
    if (group) {
      return OB11Constructor.group(group);
    } else {
      throw `群${payload.group_id}不存在`;
    }
  }
}

function _defineProperty$1j(e, r, t) {
  return (r = _toPropertyKey$1j(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1j(t) {
  var i = _toPrimitive$1j(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1j(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$G = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    no_cache: {
      type: ["boolean", "string"]
    }
  },
  required: ["group_id"]
};
class GetGroupMemberList extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1j(this, "actionName", ActionName.GetGroupMemberList);
    _defineProperty$1j(this, "PayloadSchema", SchemaData$G);
  }
  async _handle(payload) {
    const isNocache = payload.no_cache == true || payload.no_cache === "true";
    const GroupList = await NTQQGroupApi.getGroups(isNocache);
    const group = GroupList.find((item) => item.groupCode == payload.group_id);
    if (!group) {
      throw `群${payload.group_id}不存在`;
    }
    const groupMembers = await NTQQGroupApi.getGroupMembers(payload.group_id.toString());
    let _groupMembers = Array.from(groupMembers.values()).map((item) => {
      return OB11Constructor.groupMember(group.groupCode, item);
    });
    const MemberMap = /* @__PURE__ */ new Map();
    const date = Math.round(Date.now() / 1e3);
    for (let i = 0, len = _groupMembers.length; i < len; i++) {
      _groupMembers[i].join_time = date;
      _groupMembers[i].last_sent_time = date;
      MemberMap.set(_groupMembers[i].user_id, _groupMembers[i]);
    }
    if (!requireMinNTQQBuild("26702")) {
      const selfRole = groupMembers.get(selfInfo.uid)?.role;
      const isPrivilege = selfRole === 3 || selfRole === 4;
      if (isPrivilege) {
        const webGroupMembers = await WebApi.getGroupMembers(payload.group_id.toString());
        for (let i = 0, len = webGroupMembers.length; i < len; i++) {
          if (!webGroupMembers[i]?.uin) {
            continue;
          }
          const MemberData = MemberMap.get(webGroupMembers[i]?.uin);
          if (MemberData) {
            MemberData.join_time = webGroupMembers[i]?.join_time;
            MemberData.last_sent_time = webGroupMembers[i]?.last_speak_time;
            MemberData.qage = webGroupMembers[i]?.qage;
            MemberData.level = webGroupMembers[i]?.lv.level.toString();
            MemberMap.set(webGroupMembers[i]?.uin, MemberData);
          }
        }
      } else {
        if (isNocache) {
          const DateMap = await NTQQGroupApi.getGroupMemberLastestSendTimeCache(payload.group_id.toString());
          for (const DateUin of DateMap.keys()) {
            const MemberData = MemberMap.get(parseInt(DateUin));
            if (MemberData) {
              MemberData.last_sent_time = parseInt(DateMap.get(DateUin));
            }
          }
        } else {
          _groupMembers.forEach((item) => {
            item.last_sent_time = date;
            item.join_time = date;
          });
        }
      }
    } else {
      _groupMembers.forEach(async (item) => {
        item.last_sent_time = parseInt((await getGroupMember(payload.group_id.toString(), item.user_id))?.lastSpeakTime || date.toString());
        item.join_time = parseInt((await getGroupMember(payload.group_id.toString(), item.user_id))?.joinTime || date.toString());
      });
    }
    _groupMembers = Array.from(MemberMap.values());
    return _groupMembers;
  }
}

function _defineProperty$1i(e, r, t) {
  return (r = _toPropertyKey$1i(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1i(t) {
  var i = _toPrimitive$1i(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1i(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$F = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    user_id: {
      type: ["number", "string"]
    },
    no_cache: {
      type: ["boolean", "string"]
    }
  },
  required: ["group_id", "user_id"]
};
class GetGroupMemberInfo extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1i(this, "actionName", ActionName.GetGroupMemberInfo);
    _defineProperty$1i(this, "PayloadSchema", SchemaData$F);
  }
  async _handle(payload) {
    const isNocache = payload.no_cache == true || payload.no_cache === "true";
    const uid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
    if (!uid) {
      throw `Uin2Uid Error ${payload.user_id}不存在`;
    }
    const member = await NTQQGroupApi.getGroupMemberV2(payload.group_id.toString(), uid, isNocache);
    if (!member) {
      throw `群(${payload.group_id})成员${payload.user_id}不存在`;
    }
    try {
      const info = await NTQQUserApi.getUserDetailInfo(member.uid);
      logDebug("群成员详细信息结果", info);
      Object.assign(member, info);
    } catch (e) {
      logDebug("获取群成员详细信息失败, 只能返回基础信息", e);
    }
    const date = Math.round(Date.now() / 1e3);
    const retMember = OB11Constructor.groupMember(payload.group_id.toString(), member);
    if (!requireMinNTQQBuild("26702")) {
      const SelfInfoInGroup = await NTQQGroupApi.getGroupMemberV2(payload.group_id.toString(), selfInfo.uid, isNocache);
      let isPrivilege = false;
      if (SelfInfoInGroup) {
        isPrivilege = SelfInfoInGroup.role === 3 || SelfInfoInGroup.role === 4;
      }
      if (isPrivilege) {
        const webGroupMembers = await WebApi.getGroupMembers(payload.group_id.toString());
        for (let i = 0, len = webGroupMembers.length; i < len; i++) {
          if (webGroupMembers[i]?.uin && webGroupMembers[i].uin === retMember.user_id) {
            retMember.join_time = webGroupMembers[i]?.join_time;
            retMember.last_sent_time = webGroupMembers[i]?.last_speak_time;
            retMember.qage = webGroupMembers[i]?.qage;
            retMember.level = webGroupMembers[i]?.lv.level.toString();
          }
        }
      } else {
        const LastestMsgList = await NTQQGroupApi.getLastestMsg(payload.group_id.toString(), [payload.user_id.toString()]);
        if (LastestMsgList?.msgList?.length && LastestMsgList?.msgList?.length > 0) {
          const last_send_time = LastestMsgList.msgList[0].msgTime;
          if (last_send_time && last_send_time != "0" && last_send_time != "") {
            retMember.last_sent_time = parseInt(last_send_time);
            retMember.join_time = Math.round(Date.now() / 1e3);
          }
        }
      }
    } else {
      retMember.last_sent_time = parseInt((await getGroupMember(payload.group_id.toString(), retMember.user_id))?.lastSpeakTime || date.toString());
      retMember.join_time = parseInt((await getGroupMember(payload.group_id.toString(), retMember.user_id))?.joinTime || date.toString());
    }
    return retMember;
  }
}

function _defineProperty$1h(e, r, t) {
  return (r = _toPropertyKey$1h(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1h(t) {
  var i = _toPrimitive$1h(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1h(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class SendGroupMsg extends SendMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$1h(this, "actionName", ActionName.SendGroupMsg);
    _defineProperty$1h(this, "contextMode", ContextMode.Group);
  }
  async check(payload) {
    delete payload.user_id;
    payload.message_type = "group";
    return super.check(payload);
  }
}

function _defineProperty$1g(e, r, t) {
  return (r = _toPropertyKey$1g(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1g(t) {
  var i = _toPrimitive$1g(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1g(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class SendPrivateMsg extends SendMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$1g(this, "actionName", ActionName.SendPrivateMsg);
    _defineProperty$1g(this, "contextMode", ContextMode.Private);
  }
  async check(payload) {
    payload.message_type = "private";
    return super.check(payload);
  }
}

function _defineProperty$1f(e, r, t) {
  return (r = _toPropertyKey$1f(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1f(t) {
  var i = _toPrimitive$1f(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1f(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$E = {
  type: "object",
  properties: {
    message_id: {
      oneOf: [{
        type: "number"
      }, {
        type: "string"
      }]
    }
  },
  required: ["message_id"]
};
class DeleteMsg extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1f(this, "actionName", ActionName.DeleteMsg);
    _defineProperty$1f(this, "PayloadSchema", SchemaData$E);
  }
  async _handle(payload) {
    const msg = MessageUnique.getMsgIdAndPeerByShortId(Number(payload.message_id));
    if (msg) {
      const ret = NTEventDispatch.RegisterListen("NodeIKernelMsgListener/onMsgInfoListUpdate", 1, 5e3, (msgs) => {
        if (msgs.find((m) => m.msgId === msg.MsgId && m.recallTime !== "0")) {
          return true;
        }
        return false;
      }).catch((e) => new Promise((resolve, reject) => {
        resolve(void 0);
      }));
      await NTQQMsgApi.recallMsg(msg.Peer, [msg.MsgId]);
      const data = await ret;
      if (!data) {
        throw new Error("Recall failed");
      }
    }
  }
}

const version = "1.8.6";

function _defineProperty$1e(e, r, t) {
  return (r = _toPropertyKey$1e(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1e(t) {
  var i = _toPrimitive$1e(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1e(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetVersionInfo extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1e(this, "actionName", ActionName.GetVersionInfo);
  }
  async _handle(payload) {
    return {
      app_name: "NapCat.Onebot",
      protocol_version: "v11",
      app_version: version
    };
  }
}

function _defineProperty$1d(e, r, t) {
  return (r = _toPropertyKey$1d(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1d(t) {
  var i = _toPrimitive$1d(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1d(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class CanSendRecord extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1d(this, "actionName", ActionName.CanSendRecord);
  }
  async _handle(_payload) {
    return {
      yes: true
    };
  }
}

function _defineProperty$1c(e, r, t) {
  return (r = _toPropertyKey$1c(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1c(t) {
  var i = _toPrimitive$1c(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1c(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class CanSendImage extends CanSendRecord {
  constructor(...args) {
    super(...args);
    _defineProperty$1c(this, "actionName", ActionName.CanSendImage);
  }
}

function _defineProperty$1b(e, r, t) {
  return (r = _toPropertyKey$1b(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1b(t) {
  var i = _toPrimitive$1b(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1b(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetStatus extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$1b(this, "actionName", ActionName.GetStatus);
  }
  async _handle(payload) {
    return {
      online: !!selfInfo.online,
      good: true,
      stat
    };
  }
}

function _defineProperty$1a(e, r, t) {
  return (r = _toPropertyKey$1a(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1a(t) {
  var i = _toPrimitive$1a(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1a(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GoCQHTTPSendForwardMsg extends SendMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$1a(this, "actionName", ActionName.GoCQHTTP_SendForwardMsg);
  }
  async check(payload) {
    if (payload.messages) payload.message = normalize(payload.messages);
    return super.check(payload);
  }
}
class GoCQHTTPSendPrivateForwardMsg extends GoCQHTTPSendForwardMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$1a(this, "actionName", ActionName.GoCQHTTP_SendPrivateForwardMsg);
  }
}
class GoCQHTTPSendGroupForwardMsg extends GoCQHTTPSendForwardMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$1a(this, "actionName", ActionName.GoCQHTTP_SendGroupForwardMsg);
  }
}

function _defineProperty$19(e, r, t) {
  return (r = _toPropertyKey$19(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$19(t) {
  var i = _toPrimitive$19(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$19(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GoCQHTTPGetStrangerInfo extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$19(this, "actionName", ActionName.GoCQHTTP_GetStrangerInfo);
  }
  async _handle(payload) {
    if (!requireMinNTQQBuild("26702")) {
      const user_id = payload.user_id.toString();
      const extendData = await NTQQUserApi.getUserDetailInfoByUin(user_id);
      const uid = await NTQQUserApi.getUidByUin(user_id);
      if (!uid || uid.indexOf("*") != -1) {
        const ret = {
          ...extendData,
          user_id: parseInt(extendData.info.uin) || 0,
          nickname: extendData.info.nick,
          sex: OB11UserSex.unknown,
          age: extendData.info.birthday_year == 0 ? 0 : (/* @__PURE__ */ new Date()).getFullYear() - extendData.info.birthday_year,
          qid: extendData.info.qid,
          level: extendData.info.qqLevel && calcQQLevel(extendData.info.qqLevel) || 0,
          login_days: 0,
          uid: ""
        };
        return ret;
      }
      const data = {
        ...extendData,
        ...await NTQQUserApi.getUserDetailInfo(uid)
      };
      return OB11Constructor.stranger(data);
    } else {
      const user_id = payload.user_id.toString();
      const extendData = await NTQQUserApi.getUserDetailInfoByUinV2(user_id);
      const uid = await NTQQUserApi.getUidByUin(user_id);
      if (!uid || uid.indexOf("*") != -1) {
        const ret = {
          ...extendData,
          user_id: parseInt(extendData.detail.uin) || 0,
          nickname: extendData.detail.simpleInfo.coreInfo.nick,
          sex: OB11UserSex.unknown,
          age: 0,
          level: extendData.detail.commonExt.qqLevel && calcQQLevel(extendData.detail.commonExt.qqLevel) || 0,
          login_days: 0,
          uid: ""
        };
        return ret;
      }
      const data = {
        ...extendData,
        ...await NTQQUserApi.getUserDetailInfo(uid)
      };
      return OB11Constructor.stranger(data);
    }
  }
}

function _defineProperty$18(e, r, t) {
  return (r = _toPropertyKey$18(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$18(t) {
  var i = _toPrimitive$18(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$18(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$D = {
  type: "object",
  properties: {
    user_id: {
      type: ["number", "string"]
    },
    times: {
      type: ["number", "string"]
    }
  },
  required: ["user_id", "times"]
};
class SendLike extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$18(this, "actionName", ActionName.SendLike);
    _defineProperty$18(this, "PayloadSchema", SchemaData$D);
  }
  async _handle(payload) {
    try {
      const qq = payload.user_id.toString();
      const uid = await NTQQUserApi.getUidByUin(qq) || "";
      const result = await NTQQUserApi.like(uid, parseInt(payload.times?.toString()) || 1);
      if (result.result !== 0) {
        throw Error(result.errMsg);
      }
    } catch (e) {
      throw `点赞失败 ${e}`;
    }
    return null;
  }
}

function _defineProperty$17(e, r, t) {
  return (r = _toPropertyKey$17(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$17(t) {
  var i = _toPrimitive$17(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$17(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$C = {
  type: "object",
  properties: {
    flag: {
      type: "string"
    },
    approve: {
      type: ["string", "boolean"]
    },
    reason: {
      type: "string",
      nullable: true
    }
  },
  required: ["flag"]
};
class SetGroupAddRequest extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$17(this, "actionName", ActionName.SetGroupAddRequest);
    _defineProperty$17(this, "PayloadSchema", SchemaData$C);
  }
  async _handle(payload) {
    const flag = payload.flag.toString();
    const approve = payload.approve?.toString() !== "false";
    await NTQQGroupApi.handleGroupRequest(flag, approve ? GroupRequestOperateTypes.approve : GroupRequestOperateTypes.reject, payload.reason || "");
    return null;
  }
}

function _defineProperty$16(e, r, t) {
  return (r = _toPropertyKey$16(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$16(t) {
  var i = _toPrimitive$16(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$16(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$B = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    is_dismiss: {
      type: "boolean"
    }
  },
  required: ["group_id"]
};
class SetGroupLeave extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$16(this, "actionName", ActionName.SetGroupLeave);
    _defineProperty$16(this, "PayloadSchema", SchemaData$B);
  }
  async _handle(payload) {
    try {
      await NTQQGroupApi.quitGroup(payload.group_id.toString());
      deleteGroup(payload.group_id.toString());
    } catch (e) {
      logError("退群失败", e);
      throw e;
    }
  }
}

function _defineProperty$15(e, r, t) {
  return (r = _toPropertyKey$15(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$15(t) {
  var i = _toPrimitive$15(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$15(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetGuildList extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$15(this, "actionName", ActionName.GetGuildList);
  }
  async _handle(payload) {
    return null;
  }
}

function _defineProperty$14(e, r, t) {
  return (r = _toPropertyKey$14(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$14(t) {
  var i = _toPrimitive$14(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$14(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class Debug extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$14(this, "actionName", ActionName.Debug);
  }
  async _handle(payload) {
    const ntqqApi = [NTQQMsgApi, NTQQFriendApi, NTQQGroupApi, NTQQUserApi, NTQQFileApi];
    for (const ntqqApiClass of ntqqApi) {
      const method = ntqqApiClass[payload.method];
      if (method) {
        const result = method(...payload.args);
        if (method.constructor.name === "AsyncFunction") {
          return await result;
        }
        return result;
      }
    }
    throw `${payload.method}方法 不存在`;
  }
}

function _defineProperty$13(e, r, t) {
  return (r = _toPropertyKey$13(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$13(t) {
  var i = _toPrimitive$13(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$13(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$A = {
  type: "object",
  properties: {
    flag: {
      type: "string"
    },
    approve: {
      type: ["string", "boolean"]
    },
    remark: {
      type: "string"
    }
  },
  required: ["flag"]
};
class SetFriendAddRequest extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$13(this, "actionName", ActionName.SetFriendAddRequest);
    _defineProperty$13(this, "PayloadSchema", SchemaData$A);
  }
  async _handle(payload) {
    const approve = payload.approve?.toString() !== "false";
    await NTQQFriendApi.handleFriendRequest(payload.flag, approve);
    return null;
  }
}

function _defineProperty$12(e, r, t) {
  return (r = _toPropertyKey$12(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$12(t) {
  var i = _toPrimitive$12(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$12(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$z = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    enable: {
      type: ["boolean", "string"]
    }
  },
  required: ["group_id"]
};
class SetGroupWholeBan extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$12(this, "actionName", ActionName.SetGroupWholeBan);
    _defineProperty$12(this, "PayloadSchema", SchemaData$z);
  }
  async _handle(payload) {
    const enable = payload.enable?.toString() !== "false";
    await NTQQGroupApi.banGroup(payload.group_id.toString(), enable);
    return null;
  }
}

function _defineProperty$11(e, r, t) {
  return (r = _toPropertyKey$11(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$11(t) {
  var i = _toPrimitive$11(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$11(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$y = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    group_name: {
      type: "string"
    }
  },
  required: ["group_id", "group_name"]
};
class SetGroupName extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$11(this, "actionName", ActionName.SetGroupName);
    _defineProperty$11(this, "PayloadSchema", SchemaData$y);
  }
  async _handle(payload) {
    await NTQQGroupApi.setGroupName(payload.group_id.toString(), payload.group_name);
    return null;
  }
}

function _defineProperty$10(e, r, t) {
  return (r = _toPropertyKey$10(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$10(t) {
  var i = _toPrimitive$10(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$10(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$x = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    user_id: {
      type: ["number", "string"]
    },
    duration: {
      type: ["number", "string"]
    }
  },
  required: ["group_id", "user_id", "duration"]
};
class SetGroupBan extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$10(this, "actionName", ActionName.SetGroupBan);
    _defineProperty$10(this, "PayloadSchema", SchemaData$x);
  }
  async _handle(payload) {
    await NTQQGroupApi.banMember(payload.group_id.toString(), [{
      uid: await NTQQUserApi.getUidByUin(payload.user_id.toString()),
      timeStamp: parseInt(payload.duration.toString())
    }]);
    return null;
  }
}

function _defineProperty$$(e, r, t) {
  return (r = _toPropertyKey$$(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$$(t) {
  var i = _toPrimitive$$(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$$(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$w = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    user_id: {
      type: ["number", "string"]
    },
    reject_add_request: {
      type: ["boolean", "string"]
    }
  },
  required: ["group_id", "user_id"]
};
class SetGroupKick extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$$(this, "actionName", ActionName.SetGroupKick);
    _defineProperty$$(this, "PayloadSchema", SchemaData$w);
  }
  async _handle(payload) {
    const rejectReq = payload.reject_add_request?.toString() == "true";
    await NTQQGroupApi.kickMember(payload.group_id.toString(), [await NTQQUserApi.getUidByUin(payload.user_id.toString())], rejectReq);
    return null;
  }
}

function _defineProperty$_(e, r, t) {
  return (r = _toPropertyKey$_(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$_(t) {
  var i = _toPrimitive$_(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$_(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$v = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    user_id: {
      type: ["number", "string"]
    },
    enable: {
      type: "boolean"
    }
  },
  required: ["group_id", "user_id"]
};
class SetGroupAdmin extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$_(this, "actionName", ActionName.SetGroupAdmin);
    _defineProperty$_(this, "PayloadSchema", SchemaData$v);
  }
  async _handle(payload) {
    const member = await getGroupMember(payload.group_id, payload.user_id);
    const enable = payload.enable?.toString() !== "false";
    if (!member) {
      throw `群成员${payload.user_id}不存在`;
    }
    await NTQQGroupApi.setMemberRole(payload.group_id.toString(), member.uid, enable ? GroupMemberRole.admin : GroupMemberRole.normal);
    return null;
  }
}

function _defineProperty$Z(e, r, t) {
  return (r = _toPropertyKey$Z(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$Z(t) {
  var i = _toPrimitive$Z(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$Z(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$u = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    user_id: {
      type: ["number", "string"]
    },
    card: {
      type: "string"
    }
  },
  required: ["group_id", "user_id", "card"]
};
class SetGroupCard extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$Z(this, "actionName", ActionName.SetGroupCard);
    _defineProperty$Z(this, "PayloadSchema", SchemaData$u);
  }
  async _handle(payload) {
    const member = await getGroupMember(payload.group_id, payload.user_id);
    if (!member) {
      throw `群成员${payload.user_id}不存在`;
    }
    await NTQQGroupApi.setMemberCard(payload.group_id.toString(), member.uid, payload.card || "");
    return null;
  }
}

function _defineProperty$Y(e, r, t) {
  return (r = _toPropertyKey$Y(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$Y(t) {
  var i = _toPrimitive$Y(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$Y(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const GetFileBase_PayloadSchema = {
  type: "object",
  properties: {
    file: {
      type: "string"
    }
  },
  required: ["file"]
};
class GetFileBase extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$Y(this, "PayloadSchema", GetFileBase_PayloadSchema);
  }
  getElement(msg) {
    let element = msg.elements.find((e) => e.fileElement);
    if (!element) {
      element = msg.elements.find((e) => e.videoElement);
      if (element) {
        return {
          id: element.elementId,
          element: element.videoElement
        };
      } else {
        throw new Error("找不到文件");
      }
    }
    return {
      id: element.elementId,
      element: element.fileElement
    };
  }
  async _handle(payload) {
    const {
      enableLocalFile2Url
    } = ob11Config;
    let UuidData;
    try {
      UuidData = UUIDConverter.decode(payload.file);
      if (UuidData) {
        const peerUin = UuidData.high;
        const msgId = UuidData.low;
        const isGroup = await getGroup(peerUin);
        let peer;
        if (isGroup) {
          peer = {
            chatType: ChatType.group,
            peerUid: peerUin
          };
        }
        const PeerUid = await NTQQUserApi.getUidByUin(peerUin);
        if (PeerUid) {
          const isBuddy = await NTQQFriendApi.isBuddy(PeerUid);
          if (isBuddy) {
            peer = {
              chatType: ChatType.friend,
              peerUid: PeerUid
            };
          } else {
            peer = {
              chatType: ChatType.temp,
              peerUid: PeerUid
            };
          }
        }
        if (!peer) {
          throw new Error("chattype not support");
        }
        const msgList = await NTQQMsgApi.getMsgsByMsgId(peer, [msgId]);
        if (msgList.msgList.length == 0) {
          throw new Error("msg not found");
        }
        const msg = msgList.msgList[0];
        const findEle = msg.elements.find((e) => e.elementType == ElementType.VIDEO || e.elementType == ElementType.FILE || e.elementType == ElementType.PTT);
        if (!findEle) {
          throw new Error("element not found");
        }
        const downloadPath = await NTQQFileApi.downloadMedia(msgId, msg.chatType, msg.peerUid, findEle.elementId, "", "");
        const fileSize = findEle?.videoElement?.fileSize || findEle?.fileElement?.fileSize || findEle?.pttElement?.fileSize || "0";
        const fileName = findEle?.videoElement?.fileName || findEle?.fileElement?.fileName || findEle?.pttElement?.fileName || "";
        const res = {
          file: downloadPath,
          url: downloadPath,
          file_size: fileSize,
          file_name: fileName
        };
        if (enableLocalFile2Url) {
          try {
            res.base64 = await fsPromise.readFile(downloadPath, "base64");
          } catch (e) {
            throw new Error("文件下载失败. " + e);
          }
        }
        return res;
      }
    } catch {
    }
    const NTSearchNameResult = (await NTQQFileApi.searchfile([payload.file])).resultItems;
    if (NTSearchNameResult.length !== 0) {
      const MsgId = NTSearchNameResult[0].msgId;
      let peer = void 0;
      if (NTSearchNameResult[0].chatType == ChatType.group) {
        peer = {
          chatType: ChatType.group,
          peerUid: NTSearchNameResult[0].groupChatInfo[0].groupCode
        };
      }
      if (!peer) {
        throw new Error("chattype not support");
      }
      const msgList = (await NTQQMsgApi.getMsgsByMsgId(peer, [MsgId]))?.msgList;
      if (!msgList || msgList.length == 0) {
        throw new Error("msg not found");
      }
      const msg = msgList[0];
      const file = msg.elements.filter((e) => e.elementType == NTSearchNameResult[0].elemType);
      if (file.length == 0) {
        throw new Error("file not found");
      }
      const downloadPath = await NTQQFileApi.downloadMedia(msg.msgId, msg.chatType, msg.peerUid, file[0].elementId, "", "");
      const res = {
        file: downloadPath,
        url: downloadPath,
        file_size: NTSearchNameResult[0].fileSize.toString(),
        file_name: NTSearchNameResult[0].fileName
      };
      if (enableLocalFile2Url) {
        try {
          res.base64 = await fsPromise.readFile(downloadPath, "base64");
        } catch (e) {
          throw new Error("文件下载失败. " + e);
        }
      }
      return res;
    }
    throw new Error("file not found");
  }
}
const GetFile_PayloadSchema = {
  type: "object",
  properties: {
    file_id: {
      type: "string"
    },
    file: {
      type: "string"
    }
  },
  required: ["file_id"]
};
class GetFile extends GetFileBase {
  constructor(...args) {
    super(...args);
    _defineProperty$Y(this, "actionName", ActionName.GetFile);
    _defineProperty$Y(this, "PayloadSchema", GetFile_PayloadSchema);
  }
  async _handle(payload) {
    payload.file = payload.file_id;
    return super._handle(payload);
  }
}

function _defineProperty$X(e, r, t) {
  return (r = _toPropertyKey$X(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$X(t) {
  var i = _toPrimitive$X(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$X(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetImage extends GetFileBase {
  constructor(...args) {
    super(...args);
    _defineProperty$X(this, "actionName", ActionName.GetImage);
  }
}

function _defineProperty$W(e, r, t) {
  return (r = _toPropertyKey$W(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$W(t) {
  var i = _toPrimitive$W(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$W(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetRecord extends GetFileBase {
  constructor(...args) {
    super(...args);
    _defineProperty$W(this, "actionName", ActionName.GetRecord);
  }
  async _handle(payload) {
    const res = super._handle(payload);
    return res;
  }
}

function _defineProperty$V(e, r, t) {
  return (r = _toPropertyKey$V(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$V(t) {
  var i = _toPrimitive$V(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$V(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$t = {
  type: "object",
  properties: {
    user_id: {
      type: ["number", "string"]
    },
    group_id: {
      type: ["number", "string"]
    }
  }
};
class MarkMsgAsRead extends BaseAction {
  async getPeer(payload) {
    if (payload.user_id) {
      const peerUid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
      if (!peerUid) {
        throw `私聊${payload.user_id}不存在`;
      }
      const isBuddy = await NTQQFriendApi.isBuddy(peerUid);
      return {
        chatType: isBuddy ? ChatType.friend : ChatType.temp,
        peerUid
      };
    }
    if (!payload.group_id) {
      throw "缺少参数 group_id 或 user_id";
    }
    return {
      chatType: ChatType.group,
      peerUid: payload.group_id.toString()
    };
  }
  async _handle(payload) {
    const ret = await NTQQMsgApi.setMsgRead(await this.getPeer(payload));
    if (ret.result != 0) {
      throw "设置已读失败," + ret.errMsg;
    }
    return null;
  }
}
class MarkPrivateMsgAsRead extends MarkMsgAsRead {
  constructor(...args) {
    super(...args);
    _defineProperty$V(this, "PayloadSchema", SchemaData$t);
    _defineProperty$V(this, "actionName", ActionName.MarkPrivateMsgAsRead);
  }
}
class MarkGroupMsgAsRead extends MarkMsgAsRead {
  constructor(...args) {
    super(...args);
    _defineProperty$V(this, "PayloadSchema", SchemaData$t);
    _defineProperty$V(this, "actionName", ActionName.MarkGroupMsgAsRead);
  }
}
class GoCQHTTPMarkMsgAsRead extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$V(this, "actionName", ActionName.GoCQHTTP_MarkMsgAsRead);
  }
  async _handle(payload) {
    return null;
  }
}
class MarkAllMsgAsRead extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$V(this, "actionName", ActionName._MarkAllMsgAsRead);
  }
  async _handle(payload) {
    await NTQQMsgApi.markallMsgAsRead();
    return null;
  }
}

function _defineProperty$U(e, r, t) {
  return (r = _toPropertyKey$U(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$U(t) {
  var i = _toPrimitive$U(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$U(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$s = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    file: {
      type: "string"
    },
    name: {
      type: "string"
    },
    folder: {
      type: "string"
    },
    folder_id: {
      type: "string"
    }
    //临时扩展
  },
  required: ["group_id", "file", "name"]
};
class GoCQHTTPUploadGroupFile extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$U(this, "actionName", ActionName.GoCQHTTP_UploadGroupFile);
    _defineProperty$U(this, "PayloadSchema", SchemaData$s);
  }
  async _handle(payload) {
    const group = await getGroup(payload.group_id.toString());
    if (!group) {
      throw new Error(`群组${payload.group_id}不存在`);
    }
    let file = payload.file;
    if (fs$3.existsSync(file)) {
      file = `file://${file}`;
    }
    const downloadResult = await uri2local(file);
    if (!downloadResult.success) {
      throw new Error(downloadResult.errMsg);
    }
    const sendFileEle = await SendMsgElementConstructor.file(downloadResult.path, payload.name, payload.folder_id);
    await sendMsg({
      chatType: ChatType.group,
      peerUid: group.groupCode
    }, [sendFileEle], [], true);
    return null;
  }
}

function _defineProperty$T(e, r, t) {
  return (r = _toPropertyKey$T(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$T(t) {
  var i = _toPrimitive$T(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$T(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class SetAvatar extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$T(this, "actionName", ActionName.SetQQAvatar);
  }
  // 用不着复杂检测
  async check(payload) {
    if (!payload.file || typeof payload.file != "string") {
      return {
        valid: false,
        message: "file字段不能为空或者类型错误"
      };
    }
    return {
      valid: true
    };
  }
  async _handle(payload) {
    const {
      path,
      isLocal,
      errMsg,
      success
    } = await uri2local(payload.file);
    if (!success) {
      throw `头像${payload.file}设置失败,file字段可能格式不正确`;
    }
    if (path) {
      await checkFileReceived(path, 5e3);
      const ret = await NTQQUserApi.setQQAvatar(path);
      if (!isLocal) {
        fs$2.unlink(path, () => {
        });
      }
      if (!ret) {
        throw `头像${payload.file}设置失败,api无返回`;
      }
      if (ret["result"] == 1004022) {
        throw `头像${payload.file}设置失败，文件可能不是图片格式`;
      } else if (ret["result"] != 0) {
        throw `头像${payload.file}设置失败,未知的错误,${ret["result"]}:${ret["errMsg"]}`;
      }
    } else {
      if (!isLocal) {
        fs$2.unlink(path, () => {
        });
      }
      throw `头像${payload.file}设置失败,无法获取头像,文件可能不存在`;
    }
    return null;
  }
}

function _defineProperty$S(e, r, t) {
  return (r = _toPropertyKey$S(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$S(t) {
  var i = _toPrimitive$S(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$S(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$r = {
  type: "object",
  properties: {
    thread_count: {
      type: "number"
    },
    url: {
      type: "string"
    },
    base64: {
      type: "string"
    },
    name: {
      type: "string"
    },
    headers: {
      type: ["string", "array"],
      items: {
        type: "string"
      }
    }
  }
};
class GoCQHTTPDownloadFile extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$S(this, "actionName", ActionName.GoCQHTTP_DownloadFile);
    _defineProperty$S(this, "PayloadSchema", SchemaData$r);
  }
  async _handle(payload) {
    const isRandomName = !payload.name;
    const name = payload.name || randomUUID();
    const filePath = join(getTempDir(), name);
    if (payload.base64) {
      fs$3.writeFileSync(filePath, payload.base64, "base64");
    } else if (payload.url) {
      const headers = this.getHeaders(payload.headers);
      const buffer = await httpDownload({
        url: payload.url,
        headers
      });
      fs$3.writeFileSync(filePath, Buffer.from(buffer), "binary");
    } else {
      throw new Error("不存在任何文件, 无法下载");
    }
    if (fs$3.existsSync(filePath)) {
      if (isRandomName) {
        const md5 = await calculateFileMD5(filePath);
        const newPath = join(getTempDir(), md5);
        fs$3.renameSync(filePath, newPath);
        return {
          file: newPath
        };
      }
      return {
        file: filePath
      };
    } else {
      throw new Error("文件写入失败, 检查权限");
    }
  }
  getHeaders(headersIn) {
    const headers = {};
    if (typeof headersIn == "string") {
      headersIn = headersIn.split("[\\r\\n]");
    }
    if (Array.isArray(headersIn)) {
      for (const headerItem of headersIn) {
        const spilt = headerItem.indexOf("=");
        if (spilt < 0) {
          headers[headerItem] = "";
        } else {
          const key = headerItem.substring(0, spilt);
          headers[key] = headerItem.substring(0, spilt + 1);
        }
      }
    }
    if (!headers["Content-Type"]) {
      headers["Content-Type"] = "application/octet-stream";
    }
    return headers;
  }
}

function _defineProperty$R(e, r, t) {
  return (r = _toPropertyKey$R(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$R(t) {
  var i = _toPrimitive$R(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$R(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$q = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    message_seq: {
      type: "number"
    },
    count: {
      type: "number"
    },
    reverseOrder: {
      type: "boolean"
    }
  },
  required: ["group_id"]
};
class GoCQHTTPGetGroupMsgHistory extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$R(this, "actionName", ActionName.GoCQHTTP_GetGroupMsgHistory);
    _defineProperty$R(this, "PayloadSchema", SchemaData$q);
  }
  async _handle(payload) {
    const group = await getGroup(payload.group_id.toString());
    const isReverseOrder = payload.reverseOrder || true;
    const MsgCount = payload.count || 20;
    const peer = {
      chatType: ChatType.group,
      peerUid: payload.group_id.toString()
    };
    if (!group) throw `群${payload.group_id}不存在`;
    let msgList;
    if (!payload.message_seq || payload.message_seq == 0) {
      msgList = (await NTQQMsgApi.getLastestMsgByUids(peer, MsgCount)).msgList;
    } else {
      const startMsgId = MessageUnique.getMsgIdAndPeerByShortId(payload.message_seq)?.MsgId;
      if (!startMsgId) throw `消息${payload.message_seq}不存在`;
      msgList = (await NTQQMsgApi.getMsgHistory(peer, startMsgId, MsgCount)).msgList;
    }
    if (isReverseOrder) msgList.reverse();
    await Promise.all(msgList.map(async (msg) => {
      msg.id = MessageUnique.createMsg({
        guildId: "",
        chatType: msg.chatType,
        peerUid: msg.peerUid
      }, msg.msgId);
    }));
    const ob11MsgList = await Promise.all(msgList.map((msg) => OB11Constructor.message(msg)));
    return {
      "messages": ob11MsgList
    };
  }
}

function _defineProperty$Q(e, r, t) {
  return (r = _toPropertyKey$Q(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$Q(t) {
  var i = _toPrimitive$Q(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$Q(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$p = {
  type: "object",
  properties: {
    message_id: {
      type: "string"
    },
    id: {
      type: "string"
    }
  }
};
class GoCQHTTPGetForwardMsgAction extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$Q(this, "actionName", ActionName.GoCQHTTP_GetForwardMsg);
    _defineProperty$Q(this, "PayloadSchema", SchemaData$p);
  }
  async _handle(payload) {
    const msgIdMixOb11Id = payload.message_id || payload.id;
    if (!msgIdMixOb11Id) {
      throw Error("message_id or id is required");
    }
    const rootMsgId = MessageUnique.getShortIdByMsgId(msgIdMixOb11Id);
    const rootMsg = MessageUnique.getMsgIdAndPeerByShortId(rootMsgId || parseInt(msgIdMixOb11Id));
    if (!rootMsg) {
      throw Error("msg not found");
    }
    const data = await NTQQMsgApi.getMultiMsg(rootMsg.Peer, rootMsg.MsgId, rootMsg.MsgId);
    if (!data || data.result !== 0) {
      throw Error("找不到相关的聊天记录" + data?.errMsg);
    }
    const msgList = data.msgList;
    const messages = await Promise.all(msgList.map(async (msg) => {
      const resMsg = await OB11Constructor.message(msg);
      resMsg.message_id = MessageUnique.createMsg({
        guildId: "",
        chatType: msg.chatType,
        peerUid: msg.peerUid
      }, msg.msgId);
      return resMsg;
    }));
    messages.map((msg) => {
      msg.content = msg.message;
      delete msg.message;
    });
    return {
      messages
    };
  }
}

function _defineProperty$P(e, r, t) {
  return (r = _toPropertyKey$P(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$P(t) {
  var i = _toPrimitive$P(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$P(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$o = {
  type: "object",
  properties: {
    user_id: {
      type: ["number", "string"]
    },
    message_seq: {
      type: "number"
    },
    count: {
      type: "number"
    },
    reverseOrder: {
      type: "boolean"
    }
  },
  required: ["user_id"]
};
class GetFriendMsgHistory extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$P(this, "actionName", ActionName.GetFriendMsgHistory);
    _defineProperty$P(this, "PayloadSchema", SchemaData$o);
  }
  async _handle(payload) {
    const uid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
    const MsgCount = payload.count || 20;
    const isReverseOrder = payload.reverseOrder || true;
    if (!uid) throw `记录${payload.user_id}不存在`;
    const friend = await NTQQFriendApi.isBuddy(uid);
    const peer = {
      chatType: friend ? ChatType.friend : ChatType.temp,
      peerUid: uid
    };
    let msgList;
    if (!payload.message_seq || payload.message_seq == 0) {
      msgList = (await NTQQMsgApi.getLastestMsgByUids(peer, MsgCount)).msgList;
    } else {
      const startMsgId = MessageUnique.getMsgIdAndPeerByShortId(payload.message_seq)?.MsgId;
      if (!startMsgId) throw `消息${payload.message_seq}不存在`;
      msgList = (await NTQQMsgApi.getMsgHistory(peer, startMsgId, MsgCount)).msgList;
    }
    if (isReverseOrder) msgList.reverse();
    await Promise.all(msgList.map(async (msg) => {
      msg.id = MessageUnique.createMsg({
        guildId: "",
        chatType: msg.chatType,
        peerUid: msg.peerUid
      }, msg.msgId);
    }));
    const ob11MsgList = await Promise.all(msgList.map((msg) => OB11Constructor.message(msg)));
    return {
      "messages": ob11MsgList
    };
  }
}

function _defineProperty$O(e, r, t) {
  return (r = _toPropertyKey$O(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$O(t) {
  var i = _toPrimitive$O(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$O(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$n = {
  type: "object",
  properties: {
    domain: {
      type: "string"
    }
  },
  required: ["domain"]
};
class GetCookies extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$O(this, "actionName", ActionName.GetCookies);
    _defineProperty$O(this, "PayloadSchema", SchemaData$n);
  }
  async _handle(payload) {
    const cookiesObject = await NTQQUserApi.getCookies(payload.domain);
    const cookies = Object.entries(cookiesObject).map(([key, value]) => `${key}=${value}`).join("; ");
    const bkn = WebApi.genBkn(cookiesObject.p_skey);
    return {
      cookies,
      bkn
    };
  }
}

function _defineProperty$N(e, r, t) {
  return (r = _toPropertyKey$N(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$N(t) {
  var i = _toPrimitive$N(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$N(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$m = {
  type: "object",
  properties: {
    message_id: {
      type: ["string", "number"]
    },
    emoji_id: {
      type: ["string", "number"]
    }
  },
  required: ["message_id", "emoji_id"]
};
class SetMsgEmojiLike extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$N(this, "actionName", ActionName.SetMsgEmojiLike);
    _defineProperty$N(this, "PayloadSchema", SchemaData$m);
  }
  async _handle(payload) {
    const msg = MessageUnique.getMsgIdAndPeerByShortId(parseInt(payload.message_id.toString()));
    if (!msg) {
      throw new Error("msg not found");
    }
    if (!payload.emoji_id) {
      throw new Error("emojiId not found");
    }
    const msgData = (await NTQQMsgApi.getMsgsByMsgId(msg.Peer, [msg.MsgId])).msgList;
    if (!msgData || msgData.length == 0 || !msgData[0].msgSeq) {
      throw new Error("find msg by msgid error");
    }
    return await NTQQMsgApi.setEmojiLike(msg.Peer, msgData[0].msgSeq, payload.emoji_id.toString(), true);
  }
}

function _defineProperty$M(e, r, t) {
  return (r = _toPropertyKey$M(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$M(t) {
  var i = _toPrimitive$M(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$M(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetRobotUinRange extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$M(this, "actionName", ActionName.GetRobotUinRange);
  }
  async _handle(payload) {
    return await NTQQUserApi.getRobotUinRange();
  }
}

function _defineProperty$L(e, r, t) {
  return (r = _toPropertyKey$L(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$L(t) {
  var i = _toPrimitive$L(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$L(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$l = {
  type: "object",
  properties: {
    status: {
      type: "number"
    },
    extStatus: {
      type: "number"
    },
    batteryStatus: {
      type: "number"
    }
  },
  required: ["status", "extStatus", "batteryStatus"]
};
class SetOnlineStatus extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$L(this, "actionName", ActionName.SetOnlineStatus);
    _defineProperty$L(this, "PayloadSchema", SchemaData$l);
  }
  async _handle(payload) {
    const ret = await NTQQUserApi.setSelfOnlineStatus(payload.status, payload.extStatus, payload.batteryStatus);
    if (ret.result !== 0) {
      throw new Error("设置在线状态失败");
    }
    return null;
  }
}

function _defineProperty$K(e, r, t) {
  return (r = _toPropertyKey$K(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$K(t) {
  var i = _toPrimitive$K(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$K(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$k = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    }
  },
  required: ["group_id"]
};
class GetGroupNotice extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$K(this, "actionName", ActionName.GoCQHTTP_GetGroupNotice);
    _defineProperty$K(this, "PayloadSchema", SchemaData$k);
  }
  async _handle(payload) {
    const group = payload.group_id.toString();
    const ret = await WebApi.getGrouptNotice(group);
    if (!ret) {
      throw new Error("获取公告失败");
    }
    const retNotices = new Array();
    for (const key in ret.feeds) {
      const retApiNotice = ret.feeds[key];
      const retNotice = {
        // ...ret.feeds[key],
        sender_id: retApiNotice.u,
        publish_time: retApiNotice.pubt,
        message: {
          text: retApiNotice.msg.text,
          image: retApiNotice.msg.pics?.map((pic) => {
            return {
              id: pic.id,
              height: pic.h,
              width: pic.w
            };
          }) || []
        }
      };
      retNotices.push(retNotice);
    }
    return retNotices;
  }
}

function _defineProperty$J(e, r, t) {
  return (r = _toPropertyKey$J(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$J(t) {
  var i = _toPrimitive$J(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$J(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$j = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    pages: {
      type: "number"
    }
  },
  required: ["group_id", "pages"]
};
class GetGroupEssence extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$J(this, "actionName", ActionName.GoCQHTTP_GetEssenceMsg);
    _defineProperty$J(this, "PayloadSchema", SchemaData$j);
  }
  async _handle(payload) {
    const ret = await WebApi.getGroupEssenceMsg(payload.group_id.toString(), payload.pages.toString());
    if (!ret) {
      throw new Error("获取失败");
    }
    return ret;
  }
}

function _defineProperty$I(e, r, t) {
  return (r = _toPropertyKey$I(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$I(t) {
  var i = _toPrimitive$I(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$I(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$i = {
  type: "object",
  properties: {
    message_id: {
      type: "number"
    },
    group_id: {
      type: ["number", "string"]
    },
    user_id: {
      type: ["number", "string"]
    }
  },
  required: ["message_id"]
};
class ForwardSingleMsg extends BaseAction {
  async getTargetPeer(payload) {
    if (payload.user_id) {
      const peerUid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
      if (!peerUid) {
        throw new Error(`无法找到私聊对象${payload.user_id}`);
      }
      return {
        chatType: ChatType.friend,
        peerUid
      };
    }
    return {
      chatType: ChatType.group,
      peerUid: payload.group_id.toString()
    };
  }
  async _handle(payload) {
    const msg = MessageUnique.getMsgIdAndPeerByShortId(payload.message_id);
    if (!msg) {
      throw new Error(`无法找到消息${payload.message_id}`);
    }
    const peer = await this.getTargetPeer(payload);
    const ret = await NTQQMsgApi.forwardMsg(msg.Peer, peer, [msg.MsgId]);
    if (ret.result !== 0) {
      throw new Error(`转发消息失败 ${ret.errMsg}`);
    }
    return null;
  }
}
class ForwardFriendSingleMsg extends ForwardSingleMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$I(this, "PayloadSchema", SchemaData$i);
    _defineProperty$I(this, "actionName", ActionName.ForwardFriendSingleMsg);
  }
}
class ForwardGroupSingleMsg extends ForwardSingleMsg {
  constructor(...args) {
    super(...args);
    _defineProperty$I(this, "PayloadSchema", SchemaData$i);
    _defineProperty$I(this, "actionName", ActionName.ForwardGroupSingleMsg);
  }
}

function _defineProperty$H(e, r, t) {
  return (r = _toPropertyKey$H(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$H(t) {
  var i = _toPrimitive$H(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$H(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetFriendWithCategory extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$H(this, "actionName", ActionName.GetFriendsWithCategory);
  }
  async _handle(payload) {
    if (requireMinNTQQBuild("26702")) {
      return OB11Constructor.friendsV2(await NTQQFriendApi.getBuddyV2ExWithCate(true));
    } else {
      throw new Error("this ntqq version not support, must be 26702 or later");
    }
  }
}

function _defineProperty$G(e, r, t) {
  return (r = _toPropertyKey$G(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$G(t) {
  var i = _toPrimitive$G(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$G(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class SendGroupNotice extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$G(this, "actionName", ActionName.GoCQHTTP_SendGroupNotice);
  }
  async _handle(payload) {
    let UploadImage = void 0;
    if (payload.image) {
      const {
        errMsg,
        path,
        isLocal,
        success
      } = await uri2local(payload.image);
      if (!success) {
        throw `群公告${payload.image}设置失败,image字段可能格式不正确`;
      }
      if (!path) {
        throw `群公告${payload.image}设置失败,获取资源失败`;
      }
      await checkFileReceived(path, 5e3);
      const ImageUploadResult = await NTQQGroupApi.uploadGroupBulletinPic(payload.group_id.toString(), path);
      if (ImageUploadResult.errCode != 0) {
        throw `群公告${payload.image}设置失败,图片上传失败`;
      }
      if (!isLocal) {
        unlink(path, () => {
        });
      }
      UploadImage = ImageUploadResult.picInfo;
    }
    let Notice_Pinned = 0;
    let Notice_confirmRequired = 0;
    if (!payload.pinned) {
      Notice_Pinned = 0;
    }
    if (!payload.confirmRequired) {
      Notice_confirmRequired = 0;
    }
    const PublishGroupBulletinResult = await NTQQGroupApi.publishGroupBulletin(payload.group_id.toString(), payload.content, UploadImage, Notice_Pinned, Notice_confirmRequired);
    if (PublishGroupBulletinResult.result != 0) {
      throw `设置群公告失败,错误信息:${PublishGroupBulletinResult.errMsg}`;
    }
    return null;
  }
}

const __filename$4 = fileURLToPath(import.meta.url);
const __dirname$4 = dirname(__filename$4);
async function rebootWithQuickLogin(uin) {
  resolve$3(__dirname$4, "./napcat.bat");
  const batUtf8Script = resolve$3(__dirname$4, "./napcat-utf8.bat");
  const bashScript = resolve$3(__dirname$4, "./napcat.sh");
  if (process.platform === "win32") {
    const subProcess = spawn(`start ${batUtf8Script} -q ${uin}`, {
      detached: true,
      windowsHide: false,
      env: process.env,
      shell: true,
      stdio: "ignore"
    });
    subProcess.unref();
    spawn("cmd /c taskkill /t /f /pid " + pid.toString(), {
      detached: true,
      shell: true,
      stdio: "ignore"
    });
    spawn("cmd /c taskkill /t /f /pid " + ppid.toString(), {
      detached: true,
      shell: true,
      stdio: "ignore"
    });
  } else if (process.platform === "linux") {
    const subProcess = spawn(`${bashScript} -q ${uin}`, {
      detached: true,
      windowsHide: false,
      env: process.env,
      shell: true,
      stdio: "ignore"
    });
    subProcess.unref();
    exit(0);
  }
}
async function rebootWithNormolLogin() {
  resolve$3(__dirname$4, "./napcat.bat");
  const batUtf8Script = resolve$3(__dirname$4, "./napcat-utf8.bat");
  const bashScript = resolve$3(__dirname$4, "./napcat.sh");
  if (process.platform === "win32") {
    const subProcess = spawn(`start ${batUtf8Script} `, {
      detached: true,
      windowsHide: false,
      env: process.env,
      shell: true,
      stdio: "ignore"
    });
    subProcess.unref();
    spawn("cmd /c taskkill /t /f /pid " + pid.toString(), {
      detached: true,
      shell: true,
      stdio: "ignore"
    });
    spawn("cmd /c taskkill /t /f /pid " + ppid.toString(), {
      detached: true,
      shell: true,
      stdio: "ignore"
    });
  } else if (process.platform === "linux") {
    const subProcess = spawn(`${bashScript}`, {
      detached: true,
      windowsHide: false,
      env: process.env,
      shell: true
    });
    subProcess.unref();
    exit(0);
  }
}

function _defineProperty$F(e, r, t) {
  return (r = _toPropertyKey$F(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$F(t) {
  var i = _toPrimitive$F(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$F(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class Reboot extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$F(this, "actionName", ActionName.Reboot);
  }
  async _handle(payload) {
    if (payload.delay) {
      setTimeout(() => {
        rebootWithQuickLogin(selfInfo.uin);
      }, payload.delay);
    } else {
      rebootWithQuickLogin(selfInfo.uin);
    }
    return null;
  }
}
class RebootNormal extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$F(this, "actionName", ActionName.RebootNormal);
  }
  async _handle(payload) {
    if (payload.delay) {
      setTimeout(() => {
        rebootWithNormolLogin();
      }, payload.delay);
    } else {
      rebootWithNormolLogin();
    }
    return null;
  }
}

function _defineProperty$E(e, r, t) {
  return (r = _toPropertyKey$E(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$E(t) {
  var i = _toPrimitive$E(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$E(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$h = {
  type: "object",
  properties: {
    group_id: {
      type: ["number", "string"]
    },
    type: {
      enum: [WebHonorType.ALL, WebHonorType.EMOTION, WebHonorType.LEGEND, WebHonorType.PERFROMER, WebHonorType.STORONGE_NEWBI, WebHonorType.TALKACTIVE]
    }
  },
  required: ["group_id"]
};
class GetGroupHonorInfo extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$E(this, "actionName", ActionName.GetGroupHonorInfo);
    _defineProperty$E(this, "PayloadSchema", SchemaData$h);
  }
  async _handle(payload) {
    if (!payload.type) {
      payload.type = WebHonorType.ALL;
    }
    return await WebApi.getGroupHonorInfo(payload.group_id.toString(), payload.type);
  }
}

function _defineProperty$D(e, r, t) {
  return (r = _toPropertyKey$D(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$D(t) {
  var i = _toPrimitive$D(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$D(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GoCQHTTPHandleQuickAction extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$D(this, "actionName", ActionName.GoCQHTTP_HandleQuickAction);
  }
  async _handle(payload) {
    handleQuickOperation(payload.context, payload.operation).then().catch(log);
    return null;
  }
}

function _defineProperty$C(e, r, t) {
  return (r = _toPropertyKey$C(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$C(t) {
  var i = _toPrimitive$C(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$C(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetGroupSystemMsg extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$C(this, "actionName", ActionName.GetGroupSystemMsg);
  }
  async _handle(payload) {
    const SingleScreenNotifies = await NTQQGroupApi.getSingleScreenNotifies(10);
    const retData = {
      InvitedRequest: [],
      join_requests: []
    };
    for (const SSNotify of SingleScreenNotifies) {
      if (SSNotify.type == 1) {
        retData.InvitedRequest.push({
          request_id: SSNotify.seq,
          invitor_uin: await NTQQUserApi.getUinByUid(SSNotify.user1?.uid),
          invitor_nick: SSNotify.user1?.nickName,
          group_id: SSNotify.group?.groupCode,
          group_name: SSNotify.group?.groupName,
          checked: SSNotify.status === 1 ? false : true,
          actor: await NTQQUserApi.getUinByUid(SSNotify.user2?.uid) || 0
        });
      } else if (SSNotify.type == 7) {
        retData.join_requests.push({
          request_id: SSNotify.seq,
          requester_uin: await NTQQUserApi.getUinByUid(SSNotify.user1?.uid),
          requester_nick: SSNotify.user1?.nickName,
          group_id: SSNotify.group?.groupCode,
          group_name: SSNotify.group?.groupName,
          checked: SSNotify.status === 1 ? false : true,
          actor: await NTQQUserApi.getUinByUid(SSNotify.user2?.uid) || 0
        });
      }
    }
    return retData;
  }
}

function _defineProperty$B(e, r, t) {
  return (r = _toPropertyKey$B(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$B(t) {
  var i = _toPrimitive$B(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$B(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetOnlineClient extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$B(this, "actionName", ActionName.GetOnlineClient);
  }
  async _handle(payload) {
    NTQQSystemApi.getOnlineDev();
    await sleep(500);
    return DeviceList;
  }
}

function _defineProperty$A(e, r, t) {
  return (r = _toPropertyKey$A(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$A(t) {
  var i = _toPrimitive$A(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$A(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$g = {
  type: "object",
  properties: {
    image: {
      type: "string"
    }
  },
  required: ["image"]
};
class OCRImage extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$A(this, "actionName", ActionName.OCRImage);
    _defineProperty$A(this, "PayloadSchema", SchemaData$g);
  }
  async _handle(payload) {
    const {
      path,
      isLocal,
      errMsg,
      success
    } = await uri2local(payload.image);
    if (!success) {
      throw `OCR ${payload.image}失败,image字段可能格式不正确`;
    }
    if (path) {
      await checkFileReceived(path, 5e3);
      const ret = await NTQQSystemApi.ORCImage(path);
      if (!isLocal) {
        fs$3.unlink(path, () => {
        });
      }
      if (!ret) {
        throw `OCR ${payload.file}失败`;
      }
      return ret.result;
    }
    if (!isLocal) {
      fs$3.unlink(path, () => {
      });
    }
    throw `OCR ${payload.file}失败,文件可能不存在`;
  }
}
class IOCRImage extends OCRImage {
  constructor(...args) {
    super(...args);
    _defineProperty$A(this, "actionName", ActionName.IOCRImage);
  }
}

function _defineProperty$z(e, r, t) {
  return (r = _toPropertyKey$z(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$z(t) {
  var i = _toPrimitive$z(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$z(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$f = {
  type: "object",
  properties: {
    group_id: {
      type: ["string", "number"]
    }
  },
  required: ["group_id"]
};
class GetGroupFileCount extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$z(this, "actionName", ActionName.GetGroupFileCount);
    _defineProperty$z(this, "PayloadSchema", SchemaData$f);
  }
  async _handle(payload) {
    const ret = await NTQQGroupApi.GetGroupFileCount([payload.group_id?.toString()]);
    return {
      count: ret.groupFileCounts[0]
    };
  }
}

function _defineProperty$y(e, r, t) {
  return (r = _toPropertyKey$y(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$y(t) {
  var i = _toPrimitive$y(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$y(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$e = {
  type: "object",
  properties: {
    group_id: {
      type: ["string", "number"]
    },
    start_index: {
      type: "number"
    },
    file_count: {
      type: "number"
    }
  },
  required: ["group_id", "start_index", "file_count"]
};
class GetGroupFileList extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$y(this, "actionName", ActionName.GetGroupFileList);
    _defineProperty$y(this, "PayloadSchema", SchemaData$e);
  }
  async _handle(payload) {
    const ret = await NTQQMsgApi.getGroupFileList(payload.group_id.toString(), {
      sortType: 1,
      fileCount: payload.file_count,
      startIndex: payload.start_index,
      sortOrder: 2,
      showOnlinedocFolder: 0
    }).catch((e) => {
      return [];
    });
    return {
      FileList: ret
    };
  }
}

function _defineProperty$x(e, r, t) {
  return (r = _toPropertyKey$x(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$x(t) {
  var i = _toPrimitive$x(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$x(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$d = {
  type: "object",
  properties: {
    words: {
      type: "array",
      items: {
        type: "string"
      }
    }
  },
  required: ["words"]
};
class TranslateEnWordToZn extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$x(this, "actionName", ActionName.TranslateEnWordToZn);
    _defineProperty$x(this, "PayloadSchema", SchemaData$d);
  }
  async _handle(payload) {
    const ret = await NTQQSystemApi.translateEnWordToZn(payload.words);
    if (ret.result !== 0) {
      throw new Error("翻译失败");
    }
    return ret.words;
  }
}

function _defineProperty$w(e, r, t) {
  return (r = _toPropertyKey$w(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$w(t) {
  var i = _toPrimitive$w(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$w(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$c = {
  type: "object",
  properties: {
    group_id: {
      type: ["string", "number"]
    },
    folder_name: {
      type: "string"
    }
  },
  required: ["group_id", "folder_name"]
};
class SetGroupFileFolder extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$w(this, "actionName", ActionName.SetGroupFileFolder);
    _defineProperty$w(this, "PayloadSchema", SchemaData$c);
  }
  async _handle(payload) {
    return (await NTQQGroupApi.CreatGroupFileFolder(payload.group_id.toString(), payload.folder_name)).resultWithGroupItem;
  }
}

function _defineProperty$v(e, r, t) {
  return (r = _toPropertyKey$v(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$v(t) {
  var i = _toPrimitive$v(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$v(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$b = {
  type: "object",
  properties: {
    group_id: {
      type: ["string", "number"]
    },
    file_id: {
      type: "string"
    }
  },
  required: ["group_id", "file_id"]
};
class DelGroupFile extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$v(this, "actionName", ActionName.DelGroupFile);
    _defineProperty$v(this, "PayloadSchema", SchemaData$b);
  }
  async _handle(payload) {
    return await NTQQGroupApi.DelGroupFile(payload.group_id.toString(), [payload.file_id]);
  }
}

function _defineProperty$u(e, r, t) {
  return (r = _toPropertyKey$u(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$u(t) {
  var i = _toPrimitive$u(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$u(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$a = {
  type: "object",
  properties: {
    group_id: {
      type: ["string", "number"]
    },
    folder_id: {
      type: "string"
    }
  },
  required: ["group_id", "folder_id"]
};
class DelGroupFileFolder extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$u(this, "actionName", ActionName.DelGroupFileFolder);
    _defineProperty$u(this, "PayloadSchema", SchemaData$a);
  }
  async _handle(payload) {
    return (await NTQQGroupApi.DelGroupFileFolder(payload.group_id.toString(), payload.folder_id)).groupFileCommonResult;
  }
}

function _defineProperty$t(e, r, t) {
  return (r = _toPropertyKey$t(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$t(t) {
  var i = _toPrimitive$t(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$t(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$9 = {
  type: "object",
  properties: {
    nick: {
      type: "string"
    },
    longNick: {
      type: "string"
    },
    sex: {
      type: "number"
    }
    //传Sex值？建议传0 
  },
  required: ["nick", "longNick", "sex"]
};
class SetSelfProfile extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$t(this, "actionName", ActionName.SetSelfProfile);
    _defineProperty$t(this, "PayloadSchema", SchemaData$9);
  }
  async _handle(payload) {
    const ret = await NTQQUserApi.modifySelfProfile({
      nick: payload.nick,
      longNick: payload.longNick,
      sex: payload.sex,
      birthday: {
        birthday_year: "",
        birthday_month: "",
        birthday_day: ""
      },
      location: void 0
    });
    return ret;
  }
}

function _defineProperty$s(e, r, t) {
  return (r = _toPropertyKey$s(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$s(t) {
  var i = _toPrimitive$s(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$s(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$8 = {
  type: "object",
  properties: {
    user_id: {
      type: "string"
    },
    group_id: {
      type: "string"
    },
    phoneNumber: {
      type: "string"
    }
  }
};
class sharePeer extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$s(this, "actionName", ActionName.SharePeer);
    _defineProperty$s(this, "PayloadSchema", SchemaData$8);
  }
  async _handle(payload) {
    if (payload.group_id) {
      return await NTQQGroupApi.getGroupRecommendContactArkJson(payload.group_id);
    } else if (payload.user_id) {
      return await NTQQUserApi.getBuddyRecommendContactArkJson(payload.user_id, payload.phoneNumber || "");
    }
  }
}
const SchemaDataGroupEx = {
  type: "object",
  properties: {
    group_id: {
      type: "string"
    }
  },
  required: ["group_id"]
};
class shareGroupEx extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$s(this, "actionName", ActionName.ShareGroupEx);
    _defineProperty$s(this, "PayloadSchema", SchemaDataGroupEx);
  }
  async _handle(payload) {
    return await NTQQGroupApi.getArkJsonGroupShare(payload.group_id);
  }
}

class NTQQCollectionApi {
  static async createCollection(authorUin, authorUid, authorName, brief, rawData) {
    let param = {
      commInfo: {
        bid: 1,
        category: 2,
        author: {
          type: 1,
          numId: authorUin,
          strId: authorName,
          groupId: "0",
          groupName: "",
          uid: authorUid
        },
        customGroupId: "0",
        createTime: Date.now().toString(),
        sequence: Date.now().toString()
      },
      richMediaSummary: {
        originalUri: "",
        publisher: "",
        richMediaVersion: 0,
        subTitle: "",
        title: "",
        brief,
        picList: [],
        contentType: 1
      },
      richMediaContent: {
        rawData,
        bizDataList: [],
        picList: [],
        fileList: []
      },
      need_share_url: false
    };
    return napCatCore.session.getCollectionService().createNewCollectionItem(param);
  }
  static async getAllCollection(category = 0, count = 50) {
    let param = {
      category,
      groupId: -1,
      forceSync: true,
      forceFromDb: false,
      timeStamp: "0",
      count,
      searchDown: true
    };
    return napCatCore.session.getCollectionService().getCollectionItemList(param);
  }
}

function _defineProperty$r(e, r, t) {
  return (r = _toPropertyKey$r(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$r(t) {
  var i = _toPrimitive$r(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$r(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$7 = {
  type: "object",
  properties: {
    rawData: {
      type: "string"
    },
    brief: {
      type: "string"
    }
  },
  required: ["brief", "rawData"]
};
class CreateCollection extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$r(this, "actionName", ActionName.CreateCollection);
    _defineProperty$r(this, "PayloadSchema", SchemaData$7);
  }
  async _handle(payload) {
    return await NTQQCollectionApi.createCollection(selfInfo.uin, selfInfo.uid, selfInfo.nick, payload.brief, payload.rawData);
  }
}

function _defineProperty$q(e, r, t) {
  return (r = _toPropertyKey$q(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$q(t) {
  var i = _toPrimitive$q(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$q(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$6 = {
  type: "object",
  properties: {
    longNick: {
      type: "string"
    }
  },
  required: ["longNick"]
};
class SetLongNick extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$q(this, "actionName", ActionName.SetLongNick);
    _defineProperty$q(this, "PayloadSchema", SchemaData$6);
  }
  async _handle(payload) {
    const ret = await NTQQUserApi.setLongNick(payload.longNick);
    return ret;
  }
}

function _defineProperty$p(e, r, t) {
  return (r = _toPropertyKey$p(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$p(t) {
  var i = _toPrimitive$p(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$p(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$5 = {
  type: "object",
  properties: {
    message_id: {
      type: ["number", "string"]
    }
  },
  required: ["message_id"]
};
class DelEssenceMsg extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$p(this, "actionName", ActionName.DelEssenceMsg);
    _defineProperty$p(this, "PayloadSchema", SchemaData$5);
  }
  async _handle(payload) {
    const msg = await MessageUnique.getMsgIdAndPeerByShortId(parseInt(payload.message_id.toString()));
    if (!msg) {
      throw new Error("msg not found");
    }
    return await NTQQGroupApi.removeGroupEssence(msg.Peer.peerUid, msg.MsgId);
  }
}

function _defineProperty$o(e, r, t) {
  return (r = _toPropertyKey$o(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$o(t) {
  var i = _toPrimitive$o(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$o(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$4 = {
  type: "object",
  properties: {
    message_id: {
      type: ["number", "string"]
    }
  },
  required: ["message_id"]
};
class SetEssenceMsg extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$o(this, "actionName", ActionName.SetEssenceMsg);
    _defineProperty$o(this, "PayloadSchema", SchemaData$4);
  }
  async _handle(payload) {
    const msg = MessageUnique.getMsgIdAndPeerByShortId(parseInt(payload.message_id.toString()));
    if (!msg) {
      throw new Error("msg not found");
    }
    return await NTQQGroupApi.addGroupEssence(msg.Peer.peerUid, msg.MsgId);
  }
}

function _defineProperty$n(e, r, t) {
  return (r = _toPropertyKey$n(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$n(t) {
  var i = _toPrimitive$n(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$n(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$3 = {
  type: "object",
  properties: {
    count: {
      type: ["number", "string"]
    }
  }
};
class GetRecentContact extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$n(this, "actionName", ActionName.GetRecentContact);
    _defineProperty$n(this, "PayloadSchema", SchemaData$3);
  }
  async _handle(payload) {
    const ret = await NTQQUserApi.getRecentContactListSnapShot(parseInt((payload.count || 10).toString()));
    const data = await Promise.all(ret.info.changedList.map(async (t) => {
      const FastMsg = await NTQQMsgApi.getMsgsByMsgId({
        chatType: t.chatType,
        peerUid: t.peerUid
      }, [t.msgId]);
      if (FastMsg.msgList.length > 0) {
        const lastestMsg = await OB11Constructor.message(FastMsg.msgList[0]);
        return {
          lastestMsg,
          peerUin: t.peerUin,
          remark: t.remark,
          msgTime: t.msgTime,
          chatType: t.chatType,
          msgId: t.msgId,
          sendNickName: t.sendNickName,
          sendMemberName: t.sendMemberName,
          peerName: t.peerName
        };
      }
      return {
        peerUin: t.peerUin,
        remark: t.remark,
        msgTime: t.msgTime,
        chatType: t.chatType,
        msgId: t.msgId,
        sendNickName: t.sendNickName,
        sendMemberName: t.sendMemberName,
        peerName: t.peerName
      };
    }));
    return data;
  }
}

function _defineProperty$m(e, r, t) {
  return (r = _toPropertyKey$m(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$m(t) {
  var i = _toPrimitive$m(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$m(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class GetProfileLike extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$m(this, "actionName", ActionName.GetProfileLike);
  }
  async _handle(payload) {
    const ret = await NTQQUserApi.getProfileLike(selfInfo.uid);
    const listdata = ret.info.userLikeInfos[0].favoriteInfo.userInfos;
    for (let i = 0; i < listdata.length; i++) {
      listdata[i].uin = parseInt(await NTQQUserApi.getUinByUid(listdata[i].uid) || "");
    }
    return listdata;
  }
}

function _defineProperty$l(e, r, t) {
  return (r = _toPropertyKey$l(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$l(t) {
  var i = _toPrimitive$l(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$l(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class SetGroupHeader extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$l(this, "actionName", ActionName.SetGroupHeader);
  }
  // 用不着复杂检测
  async check(payload) {
    if (!payload.file || typeof payload.file != "string" || !payload.groupCode || typeof payload.groupCode != "string") {
      return {
        valid: false,
        message: "file和groupCode字段不能为空或者类型错误"
      };
    }
    return {
      valid: true
    };
  }
  async _handle(payload) {
    const {
      path,
      isLocal,
      errMsg,
      success
    } = await uri2local(payload.file);
    if (!success) {
      throw `头像${payload.file}设置失败,file字段可能格式不正确`;
    }
    if (path) {
      await checkFileReceived(path, 5e3);
      const ret = await NTQQGroupApi.setGroupAvatar(payload.groupCode, path);
      if (!isLocal) {
        fs$2.unlink(path, () => {
        });
      }
      if (!ret) {
        throw `头像${payload.file}设置失败,api无返回`;
      }
      return ret;
    } else {
      if (!isLocal) {
        fs$2.unlink(path, () => {
        });
      }
      throw `头像${payload.file}设置失败,无法获取头像,文件可能不存在`;
    }
  }
}

function _defineProperty$k(e, r, t) {
  return (r = _toPropertyKey$k(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$k(t) {
  var i = _toPrimitive$k(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$k(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$2 = {
  type: "object",
  properties: {
    count: {
      type: "number"
    }
  }
};
class FetchCustomFace extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$k(this, "actionName", ActionName.FetchCustomFace);
    _defineProperty$k(this, "PayloadSchema", SchemaData$2);
  }
  async _handle(payload) {
    const ret = await NTQQMsgApi.fetchFavEmojiList(payload.count || 48);
    return ret.emojiInfoList.map((e) => e.url);
  }
}

function _defineProperty$j(e, r, t) {
  return (r = _toPropertyKey$j(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$j(t) {
  var i = _toPrimitive$j(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$j(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData$1 = {
  type: "object",
  properties: {
    user_id: {
      type: ["number", "string"]
    },
    file: {
      type: "string"
    },
    name: {
      type: "string"
    }
  },
  required: ["user_id", "file", "name"]
};
class GoCQHTTPUploadPrivateFile extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$j(this, "actionName", ActionName.GOCQHTTP_UploadPrivateFile);
    _defineProperty$j(this, "PayloadSchema", SchemaData$1);
  }
  async getPeer(payload) {
    if (payload.user_id) {
      const peerUid = await NTQQUserApi.getUidByUin(payload.user_id.toString());
      if (!peerUid) {
        throw `私聊${payload.user_id}不存在`;
      }
      const isBuddy = await NTQQFriendApi.isBuddy(peerUid);
      return {
        chatType: isBuddy ? ChatType.friend : ChatType.temp,
        peerUid
      };
    }
    throw "缺少参数 user_id";
  }
  async _handle(payload) {
    const peer = await this.getPeer(payload);
    let file = payload.file;
    if (fs$3.existsSync(file)) {
      file = `file://${file}`;
    }
    const downloadResult = await uri2local(file);
    if (!downloadResult.success) {
      throw new Error(downloadResult.errMsg);
    }
    const sendFileEle = await SendMsgElementConstructor.file(downloadResult.path, payload.name);
    await sendMsg(peer, [sendFileEle], [], true);
    return null;
  }
}

function _defineProperty$i(e, r, t) {
  return (r = _toPropertyKey$i(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$i(t) {
  var i = _toPrimitive$i(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$i(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class TestApi01 extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$i(this, "actionName", ActionName.TestApi01);
  }
  // 用不着复杂检测
  async check(payload) {
    return {
      valid: true
    };
  }
  async _handle(payload) {
    return await napCatCore.session.getMsgService().sendSsoCmdReqByContend(payload.cmd, payload.param);
  }
}

function _defineProperty$h(e, r, t) {
  return (r = _toPropertyKey$h(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$h(t) {
  var i = _toPrimitive$h(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$h(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const SchemaData = {
  type: "object",
  properties: {
    user_id: {
      type: "string"
    },
    group_id: {
      type: "string"
    },
    emojiId: {
      type: "string"
    },
    emojiType: {
      type: "string"
    },
    message_id: {
      type: ["string", "number"]
    },
    count: {
      type: "number"
    }
  },
  required: ["emojiId", "emojiType", "message_id"]
};
class FetchEmojioLike extends BaseAction {
  constructor(...args) {
    super(...args);
    _defineProperty$h(this, "actionName", ActionName.FetchEmojioLike);
    _defineProperty$h(this, "PayloadSchema", SchemaData);
  }
  async _handle(payload) {
    const msgIdPeer = MessageUnique.getMsgIdAndPeerByShortId(parseInt(payload.message_id.toString()));
    if (!msgIdPeer) throw new Error("消息不存在");
    const msg = (await NTQQMsgApi.getMsgsByMsgId(msgIdPeer.Peer, [msgIdPeer.MsgId])).msgList[0];
    const ret = await NTQQMsgApi.getMsgEmojiLikesList(msgIdPeer.Peer, msg.msgSeq, payload.emojiId, payload.emojiType, payload.count);
    return ret;
  }
}

const actionHandlers = [
  new FetchEmojioLike(),
  new RebootNormal(),
  new GetFile(),
  new Debug(),
  new Reboot(),
  new SetSelfProfile(),
  new shareGroupEx(),
  new sharePeer(),
  new CreateCollection(),
  new SetLongNick(),
  new ForwardFriendSingleMsg(),
  new ForwardGroupSingleMsg(),
  new MarkGroupMsgAsRead(),
  new MarkPrivateMsgAsRead(),
  new SetAvatar(),
  new TranslateEnWordToZn(),
  new GetGroupFileCount(),
  new GetGroupFileList(),
  new SetGroupFileFolder(),
  new DelGroupFile(),
  new DelGroupFileFolder(),
  // onebot11
  new SendLike(),
  new GetMsg(),
  new GetLoginInfo(),
  new GetFriendList(),
  new GetGroupList(),
  new GetGroupInfo(),
  new GetGroupMemberList(),
  new GetGroupMemberInfo(),
  new SendGroupMsg(),
  new SendPrivateMsg(),
  new SendMsg(),
  new DeleteMsg(),
  new SetGroupAddRequest(),
  new SetFriendAddRequest(),
  new SetGroupLeave(),
  new GetVersionInfo(),
  new CanSendRecord(),
  new CanSendImage(),
  new GetStatus(),
  new SetGroupWholeBan(),
  new SetGroupBan(),
  new SetGroupKick(),
  new SetGroupAdmin(),
  new SetGroupName(),
  new SetGroupCard(),
  new GetImage(),
  new GetRecord(),
  new SetMsgEmojiLike(),
  new GetCookies(),
  new SetOnlineStatus(),
  new GetRobotUinRange(),
  new GetFriendWithCategory(),
  //以下为go-cqhttp api
  new GetOnlineClient(),
  new OCRImage(),
  new IOCRImage(),
  new GetGroupHonorInfo(),
  new SendGroupNotice(),
  new GetGroupNotice(),
  new GetGroupEssence(),
  new GoCQHTTPSendForwardMsg(),
  new GoCQHTTPSendGroupForwardMsg(),
  new GoCQHTTPSendPrivateForwardMsg(),
  new GoCQHTTPGetStrangerInfo(),
  new GoCQHTTPDownloadFile(),
  new GetGuildList(),
  new GoCQHTTPMarkMsgAsRead(),
  new GoCQHTTPUploadGroupFile(),
  new GoCQHTTPGetGroupMsgHistory(),
  new GoCQHTTPGetForwardMsgAction(),
  new GetFriendMsgHistory(),
  new GoCQHTTPHandleQuickAction(),
  new GetGroupSystemMsg(),
  new DelEssenceMsg(),
  new SetEssenceMsg(),
  new GetRecentContact(),
  new MarkAllMsgAsRead(),
  new GetProfileLike(),
  new SetGroupHeader(),
  new FetchCustomFace(),
  new GoCQHTTPUploadPrivateFile(),
  new TestApi01()
];
function initActionMap() {
  const actionMap2 = /* @__PURE__ */ new Map();
  for (const action of actionHandlers) {
    actionMap2.set(action.actionName, action);
    actionMap2.set(action.actionName + "_async", action);
    actionMap2.set(action.actionName + "_rate_limited", action);
  }
  return actionMap2;
}
const actionMap = initActionMap();

function _defineProperty$g(e, r, t) {
  return (r = _toPropertyKey$g(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$g(t) {
  var i = _toPrimitive$g(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$g(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11BaseMetaEvent extends OB11BaseEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$g(this, "post_type", EventType.META);
    _defineProperty$g(this, "meta_event_type", void 0);
  }
}

function _defineProperty$f(e, r, t) {
  return (r = _toPropertyKey$f(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$f(t) {
  var i = _toPrimitive$f(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$f(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11HeartbeatEvent extends OB11BaseMetaEvent {
  constructor(isOnline, isGood, interval) {
    super();
    _defineProperty$f(this, "meta_event_type", "heartbeat");
    _defineProperty$f(this, "status", void 0);
    _defineProperty$f(this, "interval", void 0);
    this.interval = interval;
    this.status = {
      online: isOnline,
      good: isGood
    };
  }
}

function _defineProperty$e(e, r, t) {
  return (r = _toPropertyKey$e(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$e(t) {
  var i = _toPrimitive$e(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$e(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11HTTPServer extends HttpServerBase {
  constructor(...args) {
    super(...args);
    _defineProperty$e(this, "name", "OneBot V11 server");
  }
  handleFailed(res, payload, e) {
    res.send(OB11Response.error(e?.stack?.toString() || e.message || "Error Handle", 200));
  }
  listen(port, host) {
    if (ob11Config.http.enable) {
      super.listen(port, host);
    }
  }
}
const ob11HTTPServer = new OB11HTTPServer();
setTimeout(() => {
  for (const [actionName, action] of actionMap) {
    for (const method of ["post", "get"]) {
      ob11HTTPServer.registerRouter(method, actionName, (res, payload) => {
        return action.handle(payload);
      });
    }
  }
}, 0);
class HTTPHeart {
  constructor() {
    _defineProperty$e(this, "intervalId", null);
  }
  start(NewHeartInterval = void 0) {
    let {
      heartInterval
    } = ob11Config;
    if (NewHeartInterval && !Number.isNaN(NewHeartInterval)) {
      heartInterval = NewHeartInterval;
    }
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    this.intervalId = setInterval(() => {
      postOB11Event(new OB11HeartbeatEvent(!!selfInfo.online, true, heartInterval), false, false);
    }, heartInterval);
  }
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
}
const httpHeart = new HTTPHeart();

function _defineProperty$d(e, r, t) {
  return (r = _toPropertyKey$d(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$d(t) {
  var i = _toPrimitive$d(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$d(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
let LifeCycleSubType = /* @__PURE__ */ function(LifeCycleSubType2) {
  LifeCycleSubType2["ENABLE"] = "enable";
  LifeCycleSubType2["DISABLE"] = "disable";
  LifeCycleSubType2["CONNECT"] = "connect";
  return LifeCycleSubType2;
}({});
class OB11LifeCycleEvent extends OB11BaseMetaEvent {
  constructor(subType) {
    super();
    _defineProperty$d(this, "meta_event_type", "lifecycle");
    _defineProperty$d(this, "sub_type", void 0);
    this.sub_type = subType;
  }
}

function _defineProperty$c(e, r, t) {
  return (r = _toPropertyKey$c(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$c(t) {
  var i = _toPrimitive$c(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$c(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class WebsocketServerBase {
  constructor() {
    _defineProperty$c(this, "ws", null);
    _defineProperty$c(this, "token", "");
  }
  start(port, host = "") {
    if (port instanceof http$2.Server) {
      try {
        const wss = new WebSocketServer({
          noServer: true,
          maxPayload: 1024 * 1024 * 1024
        }).on("error", () => {
        });
        this.ws = wss;
        port.on("upgrade", function upgrade(request, socket, head) {
          wss.handleUpgrade(request, socket, head, function done(ws) {
            wss.emit("connection", ws, request);
          });
        });
        log("ws服务启动成功, 绑定到HTTP服务");
      } catch (e) {
        throw Error("ws服务启动失败, 可能是绑定的HTTP服务异常" + e.toString());
      }
    } else {
      try {
        this.ws = new WebSocketServer({
          port,
          host: "",
          maxPayload: 1024 * 1024 * 1024
        }).on("error", () => {
        });
        log(`ws服务启动成功, ${host}:${port}`);
      } catch (e) {
        throw Error("ws服务启动失败, 请检查监听的ip和端口" + e.toString());
      }
    }
    this.ws.on("connection", (wsClient, req) => {
      const url = req.url.split("?").shift() || "/";
      this.authorize(wsClient, req);
      this.onConnect(wsClient, url, req);
      wsClient.on("message", async (msg) => {
        this.onMessage(wsClient, url, msg.toString());
      });
    });
  }
  stop() {
    if (this.ws) {
      this.ws.close((err) => {
        if (err) log("ws server close failed!", err);
      });
      this.ws = null;
    }
  }
  restart(port) {
    this.stop();
    this.start(port);
  }
  authorize(wsClient, req) {
    const url = req.url.split("?").shift();
    log("ws connect", url);
    let clientToken = "";
    const authHeader = req.headers["authorization"];
    if (authHeader) {
      clientToken = authHeader.split("Bearer ").pop() || "";
      log("receive ws header token", clientToken);
    } else {
      const parsedUrl = urlParse.parse(req.url || "/", true);
      const urlToken = parsedUrl.query.access_token;
      if (urlToken) {
        if (Array.isArray(urlToken)) {
          clientToken = urlToken[0];
        } else {
          clientToken = urlToken;
        }
        log("receive ws url token", clientToken);
      }
    }
    if (this.token && clientToken != this.token) {
      this.authorizeFailed(wsClient);
      return wsClient.close();
    }
  }
  authorizeFailed(wsClient) {
  }
  onConnect(wsClient, url, req) {
  }
  onMessage(wsClient, url, msg) {
  }
  sendHeart() {
  }
}

class OB11WebsocketServer extends WebsocketServerBase {
  start(port, host = "") {
    this.token = ob11Config.token;
    super.start(port, host);
  }
  authorizeFailed(wsClient) {
    wsClient.send(JSON.stringify(OB11Response.res(null, "failed", 1403, "token验证失败")));
  }
  async handleAction(wsClient, actionName, params, echo) {
    const action = actionMap.get(actionName);
    if (!action) {
      return wsReply(wsClient, OB11Response.error("不支持的api " + actionName, 1404, echo));
    }
    try {
      const handleResult = await action.websocketHandle(params, echo);
      wsReply(wsClient, handleResult);
    } catch (e) {
      wsReply(wsClient, OB11Response.error(`api处理出错:${e.stack}`, 1200, echo));
    }
  }
  onConnect(wsClient, url, req) {
    if (url == "/api" || url == "/api/" || url == "/") {
      wsClient.on("message", async (msg) => {
        let receiveData = {
          action: "",
          params: {}
        };
        let echo = null;
        try {
          receiveData = JSON.parse(msg.toString());
          echo = receiveData.echo;
          logDebug("收到正向Websocket消息", receiveData);
        } catch (e) {
          return wsReply(wsClient, OB11Response.error("json解析失败，请检查数据格式", 1400, echo));
        }
        receiveData.params = receiveData?.params ? receiveData.params : {};
        this.handleAction(wsClient, receiveData.action, receiveData.params, receiveData.echo).then();
      });
    }
    if (url == "/event" || url == "/event/" || url == "/") {
      registerWsEventSender(wsClient);
      logDebug("event上报ws客户端已连接");
      try {
        wsReply(wsClient, new OB11LifeCycleEvent(LifeCycleSubType.CONNECT));
      } catch (e) {
        logError("发送生命周期失败", e);
      }
      const {
        heartInterval
      } = ob11Config;
      const wsClientInterval = setInterval(() => {
        wsReply(wsClient, new OB11HeartbeatEvent(!!selfInfo.online, true, heartInterval));
      }, heartInterval);
      wsClient.on("close", () => {
        logError("event上报ws客户端已断开");
        clearInterval(wsClientInterval);
        unregisterWsEventSender(wsClient);
      });
    }
  }
}
const ob11WebsocketServer = new OB11WebsocketServer();

function _defineProperty$b(e, r, t) {
  return (r = _toPropertyKey$b(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$b(t) {
  var i = _toPrimitive$b(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$b(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
let rwsList = [];
class ReverseWebsocket {
  constructor(url) {
    _defineProperty$b(this, "websocket", void 0);
    _defineProperty$b(this, "url", void 0);
    _defineProperty$b(this, "running", false);
    _defineProperty$b(this, "onclose", () => {
      logError("反向ws断开", this.url);
      unregisterWsEventSender(this.websocket);
      if (this.running) {
        this.reconnect();
      }
    });
    this.url = url;
    this.running = true;
    this.connect();
  }
  stop() {
    this.running = false;
    this.websocket.close();
  }
  onopen() {
    wsReply(this.websocket, new OB11LifeCycleEvent(LifeCycleSubType.CONNECT));
  }
  async onmessage(msg) {
    let receiveData = {
      action: void 0,
      params: {}
    };
    let echo = null;
    try {
      receiveData = JSON.parse(msg.toString());
      echo = receiveData.echo;
    } catch (e) {
      return wsReply(this.websocket, OB11Response.error("json解析失败，请检查数据格式", 1400, echo));
    }
    const action = actionMap.get(receiveData.action);
    if (!action) {
      return wsReply(this.websocket, OB11Response.error("不支持的api " + receiveData.action, 1404, echo));
    }
    try {
      receiveData.params = receiveData?.params ? receiveData.params : {};
      const handleResult = await action.websocketHandle(receiveData.params, echo);
      wsReply(this.websocket, handleResult);
    } catch (e) {
      wsReply(this.websocket, OB11Response.error(`api处理出错:${e}`, 1200, echo));
    }
  }
  send(msg) {
    if (this.websocket && this.websocket.readyState == WebSocket.OPEN) {
      this.websocket.send(msg);
    }
  }
  reconnect() {
    setTimeout(() => {
      this.connect();
    }, 3e3);
  }
  connect() {
    const {
      token,
      heartInterval
    } = ob11Config;
    this.websocket = new WebSocket$1(this.url, {
      maxPayload: 1024 * 1024 * 1024,
      handshakeTimeout: 2e3,
      perMessageDeflate: false,
      headers: {
        "X-Self-ID": selfInfo.uin,
        "Authorization": `Bearer ${token}`,
        "x-client-role": "Universal",
        // koishi-adapter-onebot 需要这个字段
        "User-Agent": "OneBot/11"
      }
    });
    registerWsEventSender(this.websocket);
    logDebug("Trying to connect to the websocket server: " + this.url);
    this.websocket.on("open", () => {
      logDebug("Connected to the websocket server: " + this.url);
      this.onopen();
    });
    this.websocket.on("message", async (data) => {
      await this.onmessage(data.toString());
    });
    this.websocket.on("error", log);
    const wsClientInterval = setInterval(() => {
      wsReply(this.websocket, new OB11HeartbeatEvent(!!selfInfo.online, true, heartInterval));
    }, heartInterval);
    this.websocket.on("close", () => {
      clearInterval(wsClientInterval);
      logDebug("The websocket connection: " + this.url + " closed, trying reconnecting...");
      this.onclose();
    });
  }
}
class OB11ReverseWebsockets {
  start() {
    for (const url of ob11Config.reverseWs.urls) {
      log("开始连接反向ws", url);
      new Promise(() => {
        try {
          rwsList.push(new ReverseWebsocket(url));
        } catch (e) {
          logError(e.stack);
        }
      }).then();
    }
  }
  stop() {
    for (const rws of rwsList) {
      rws.stop();
    }
    rwsList = [];
  }
  restart() {
    this.stop();
    this.start();
  }
}
const ob11ReverseWebsockets = new OB11ReverseWebsockets();

function _defineProperty$a(e, r, t) {
  return (r = _toPropertyKey$a(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$a(t) {
  var i = _toPrimitive$a(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$a(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11FriendRequestEvent extends OB11BaseNoticeEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$a(this, "post_type", EventType.REQUEST);
    _defineProperty$a(this, "user_id", 0);
    _defineProperty$a(this, "request_type", "friend");
    _defineProperty$a(this, "comment", "");
    _defineProperty$a(this, "flag", "");
  }
}

function _defineProperty$9(e, r, t) {
  return (r = _toPropertyKey$9(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$9(t) {
  var i = _toPrimitive$9(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$9(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupRequestEvent extends OB11GroupNoticeEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$9(this, "post_type", EventType.REQUEST);
    _defineProperty$9(this, "request_type", "group");
    _defineProperty$9(this, "sub_type", "add");
    _defineProperty$9(this, "comment", "");
    _defineProperty$9(this, "flag", "");
  }
}

function _defineProperty$8(e, r, t) {
  return (r = _toPropertyKey$8(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$8(t) {
  var i = _toPrimitive$8(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$8(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupAdminNoticeEvent extends OB11GroupNoticeEvent {
  constructor(...args) {
    super(...args);
    _defineProperty$8(this, "notice_type", "group_admin");
    _defineProperty$8(this, "sub_type", "set");
  }
  // "set" | "unset"
}

function _defineProperty$7(e, r, t) {
  return (r = _toPropertyKey$7(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$7(t) {
  var i = _toPrimitive$7(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$7(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11FriendRecallNoticeEvent extends OB11BaseNoticeEvent {
  constructor(userId, messageId) {
    super();
    _defineProperty$7(this, "notice_type", "friend_recall");
    _defineProperty$7(this, "user_id", void 0);
    _defineProperty$7(this, "message_id", void 0);
    this.user_id = userId;
    this.message_id = messageId;
  }
}

function _defineProperty$6(e, r, t) {
  return (r = _toPropertyKey$6(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$6(t) {
  var i = _toPrimitive$6(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$6(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11GroupRecallNoticeEvent extends OB11GroupNoticeEvent {
  constructor(groupId, userId, operatorId, messageId) {
    super();
    _defineProperty$6(this, "notice_type", "group_recall");
    _defineProperty$6(this, "operator_id", void 0);
    _defineProperty$6(this, "message_id", void 0);
    this.group_id = groupId;
    this.user_id = userId;
    this.operator_id = operatorId;
    this.message_id = messageId;
  }
}

const spSegColor = chalk.blue;
const spColor = chalk.cyan;
async function logMessage(ob11Message) {
  const isSelfSent = ob11Message.sender.user_id.toString() === selfInfo.uin;
  let prefix = "";
  let group;
  if (isSelfSent) {
    prefix = "发送消息 ";
    if (ob11Message.message_type === "private") {
      prefix += "给私聊 ";
      prefix += `${ob11Message.target_id}`;
    } else {
      prefix += "给群聊 ";
    }
  }
  if (ob11Message.message_type === "group") {
    if (ob11Message.group_id == 284840486) {
      group = await getGroup(ob11Message.group_id);
      prefix += "转发消息[外部来源] ";
    } else {
      group = await getGroup(ob11Message.group_id);
      prefix += `群[${group?.groupName}(${ob11Message.group_id})] `;
    }
  }
  let msgChain = "";
  if (Array.isArray(ob11Message.message)) {
    const msgParts = [];
    for (const segment of ob11Message.message) {
      if (segment.type === "text") {
        msgParts.push(segment.data.text);
      } else if (segment.type === "at") {
        const groupMember = await getGroupMember(ob11Message.group_id, segment.data.qq);
        msgParts.push(spSegColor(`[@${groupMember?.cardName || groupMember?.nick}(${segment.data.qq})]`));
      } else if (segment.type === "reply") {
        msgParts.push(spSegColor(`[回复消息|id:${segment.data.id}]`));
      } else if (segment.type === "image") {
        msgParts.push(spSegColor(`[图片|${segment.data.url}]`));
      } else if (segment.type === "face") {
        msgParts.push(spSegColor(`[表情|id:${segment.data.id}]`));
      } else if (segment.type === "mface") {
        msgParts.push(spSegColor(`[商城表情|${segment.data.url}]`));
      } else if (segment.type === "record") {
        msgParts.push(spSegColor(`[语音|${segment.data.file}]`));
      } else if (segment.type === "file") {
        msgParts.push(spSegColor(`[文件|${segment.data.file}]`));
      } else if (segment.type === "json") {
        msgParts.push(spSegColor(`[json|${JSON.stringify(segment.data)}]`));
      } else if (segment.type === "markdown") {
        msgParts.push(spSegColor(`[markdown|${segment.data.content}]`));
      } else if (segment.type === "video") {
        msgParts.push(spSegColor(`[视频|${segment.data.url}]`));
      } else if (segment.type === "forward") {
        msgParts.push(spSegColor(`[转发|${segment.data.id}|消息开始]`));
        segment.data.content.forEach((msg) => {
          logMessage(msg);
        });
        msgParts.push(spSegColor(`[转发|${segment.data.id}|消息结束]`));
      } else {
        msgParts.push(spSegColor(`[未实现|${JSON.stringify(segment)}]`));
      }
    }
    msgChain = msgParts.join(" ");
  } else {
    msgChain = ob11Message.message;
  }
  let msgString = `${prefix}${ob11Message.sender.nickname}(${ob11Message.sender.user_id}): ${msgChain}`;
  if (isSelfSent) {
    msgString = `${prefix}: ${msgChain}`;
  }
  log(msgString);
}
async function logNotice(ob11Notice) {
  log(spColor("[Notice]"), ob11Notice);
}
async function logRequest(ob11Request) {
  log(spColor("[Request]"), ob11Request);
}

function _defineProperty$5(e, r, t) {
  return (r = _toPropertyKey$5(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$5(t) {
  var i = _toPrimitive$5(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$5(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class OB11InputStatusEvent extends OB11BaseNoticeEvent {
  constructor(user_id, eventType, status_text) {
    super();
    _defineProperty$5(this, "notice_type", "notify");
    _defineProperty$5(this, "sub_type", "input_status");
    _defineProperty$5(this, "status_text", "对方正在输入...");
    _defineProperty$5(this, "event_type", 1);
    _defineProperty$5(this, "user_id", 0);
    this.user_id = user_id;
    this.event_type = eventType;
    this.status_text = status_text;
  }
}

function _defineProperty$4(e, r, t) {
  return (r = _toPropertyKey$4(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$4(t) {
  var i = _toPrimitive$4(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$4(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const DeviceList = new Array();
function check_http_ws_equal(conf) {
  return isEqual(conf.http.port, conf.ws.port) && isEqual(conf.http.host, conf.ws.host);
}
class NapCatOnebot11 {
  // 秒
  constructor() {
    _defineProperty$4(this, "bootTime", Date.now() / 1e3);
    napCatCore.onLoginSuccess(this.onReady.bind(this));
  }
  onReady() {
    logDebug("ob11 ready");
    ob11Config.read();
    const serviceInfo = `
    HTTP服务 ${ob11Config.http.enable ? "已启动" : "未启动"}, ${ob11Config.http.host}:${ob11Config.http.port}
    HTTP上报服务 ${ob11Config.http.enablePost ? "已启动" : "未启动"}, 上报地址: ${ob11Config.http.postUrls}
    WebSocket服务 ${ob11Config.ws.enable ? "已启动" : "未启动"}, ${ob11Config.ws.host}:${ob11Config.ws.port}
    WebSocket反向服务 ${ob11Config.reverseWs.enable ? "已启动" : "未启动"}, 反向地址: ${ob11Config.reverseWs.urls}
    `;
    log(serviceInfo);
    NTQQUserApi.getUserDetailInfo(selfInfo.uid).then((user) => {
      selfInfo.nick = user.nick;
      setLogSelfInfo(selfInfo);
    }).catch(logError);
    if (ob11Config.http.enable) {
      ob11HTTPServer.start(ob11Config.http.port, ob11Config.http.host);
    }
    if (ob11Config.ws.enable) {
      if (check_http_ws_equal(ob11Config) && ob11HTTPServer.server) {
        ob11WebsocketServer.start(ob11HTTPServer.server);
      } else {
        ob11WebsocketServer.start(ob11Config.ws.port, ob11Config.ws.host);
      }
    }
    if (ob11Config.reverseWs.enable) {
      ob11ReverseWebsockets.start();
    }
    if (ob11Config.http.enableHeart) {
      httpHeart.start();
    }
    const msgListener = new MsgListener();
    msgListener.onInputStatusPush = async (data) => {
      const uin = await NTQQUserApi.getUinByUid(data.fromUin);
      logNotice(`[输入状态] ${uin} ${data.statusText}`);
      postOB11Event(new OB11InputStatusEvent(parseInt(uin), data.eventType, data.statusText));
    };
    msgListener.onRecvSysMsg = async (protobufData) => {
    };
    msgListener.onKickedOffLine = (Info) => {
      selfInfo.online = false;
    };
    msgListener.onTempChatInfoUpdate = (tempChatInfo) => {
    };
    msgListener.onRecvMsg = async (msg) => {
      for (const m of msg) {
        if (this.bootTime > parseInt(m.msgTime)) {
          logDebug(`消息时间${m.msgTime}早于启动时间${this.bootTime}，忽略上报`);
          continue;
        }
        new Promise((resolve) => {
          m.id = MessageUnique.createMsg({
            chatType: m.chatType,
            peerUid: m.peerUid,
            guildId: ""
          }, m.msgId);
          this.postReceiveMsg([m]).then().catch(logError);
        }).then();
      }
    };
    msgListener.onMsgInfoListUpdate = (msgList) => {
      this.postRecallMsg(msgList).then().catch(logError);
      for (const msg of msgList.filter((e) => e.senderUin == selfInfo.uin)) {
        if (msg.sendStatus == 2) {
          OB11Constructor.message(msg).then((_msg) => {
            _msg.target_id = parseInt(msg.peerUin);
            if (ob11Config.reportSelfMessage) {
              msg.id = MessageUnique.createMsg({
                chatType: msg.chatType,
                peerUid: msg.peerUid,
                guildId: ""
              }, msg.msgId);
              this.postReceiveMsg([msg]).then().catch(logError);
            } else {
              logMessage(_msg).then().catch(logError);
            }
          }).catch(logError);
        }
      }
    };
    msgListener.onAddSendMsg = (msg) => {
    };
    napCatCore.addListener(msgListener);
    logDebug("ob11 msg listener added");
    const buddyListener = new BuddyListener();
    buddyListener.onBuddyReqChange = (req) => {
      this.postFriendRequest(req.buddyReqs).then().catch(logError);
    };
    napCatCore.addListener(buddyListener);
    logDebug("ob11 buddy listener added");
    const groupListener = new GroupListener();
    groupListener.onGroupNotifiesUpdated = async (doubt, notifies) => {
      if (![GroupNotifyTypes.ADMIN_SET, GroupNotifyTypes.ADMIN_UNSET, GroupNotifyTypes.ADMIN_UNSET_OTHER].includes(notifies[0].type)) {
        this.postGroupNotifies(notifies).then().catch((e) => logError("postGroupNotifies error: ", e));
      }
    };
    groupListener.onMemberInfoChange = async (groupCode, changeType, members) => {
      if (changeType === 1) {
        let member;
        for (const [key, value] of members) {
          member = value;
          break;
        }
        if (member) {
          const existMembers = groupMembers.get(groupCode);
          if (existMembers) {
            const existMember = existMembers.get(member.uid);
            if (existMember) {
              if (existMember.isChangeRole) {
                const notify = [{
                  time: Date.now(),
                  seq: (Date.now() * 1e3 * 1e3).toString(),
                  type: member.role === GroupMemberRole.admin ? GroupNotifyTypes.ADMIN_SET : GroupNotifyTypes.ADMIN_UNSET_OTHER,
                  // 8 设置; 13 取消
                  status: 0,
                  group: {
                    groupCode,
                    groupName: ""
                  },
                  user1: {
                    uid: member.uid,
                    nickName: member.nick
                  },
                  user2: {
                    uid: member.uid,
                    nickName: member.nick
                  },
                  actionUser: {
                    uid: "",
                    nickName: ""
                  },
                  actionTime: "0",
                  invitationExt: {
                    srcType: 0,
                    groupCode: "0",
                    waitStatus: 0
                  },
                  postscript: "",
                  repeatSeqs: [],
                  warningTips: ""
                }];
                this.postGroupNotifies(notify).then().catch((e) => logError("postGroupNotifies error: ", e));
              }
            }
          }
        }
      }
      (await getGroupMember(groupCode, selfInfo.uin))?.role;
      for (const member of members.values()) {
      }
    };
    groupListener.onJoinGroupNotify = (...notify) => {
    };
    groupListener.onGroupListUpdate = (updateType, groupList) => {
    };
    napCatCore.addListener(groupListener);
    logDebug("ob11 group listener added");
  }
  async postReceiveMsg(msgList) {
    const {
      debug,
      reportSelfMessage
    } = ob11Config;
    for (const message of msgList) {
      logDebug("收到新消息", message);
      OB11Constructor.message(message).then((msg) => {
        logDebug("收到消息: ", msg);
        if (debug) {
          msg.raw = message;
        } else {
          if (msg.message.length === 0) {
            return;
          }
        }
        if (msg.post_type === "message") {
          logMessage(msg).then().catch(logError);
        } else if (msg.post_type === "notice") {
          logNotice(msg).then().catch(logError);
        } else if (msg.post_type === "request") {
          logRequest(msg).then().catch(logError);
        }
        const isSelfMsg = msg.user_id.toString() == selfInfo.uin;
        if (isSelfMsg && !reportSelfMessage) {
          return;
        }
        if (isSelfMsg) {
          msg.target_id = parseInt(message.peerUin);
        }
        postOB11Event(msg);
      }).catch((e) => logError("constructMessage error: ", e));
      OB11Constructor.GroupEvent(message).then((groupEvent) => {
        if (groupEvent) {
          postOB11Event(groupEvent);
        }
      }).catch((e) => logError("constructGroupEvent error: ", e));
      OB11Constructor.PrivateEvent(message).then((privateEvent) => {
        if (privateEvent) {
          postOB11Event(privateEvent);
        }
      });
    }
  }
  async SetConfig(NewOb11) {
    try {
      const OldConfig = JSON.parse(JSON.stringify(ob11Config));
      ob11Config.save(NewOb11, true);
      const isHttpChanged = !isEqual(NewOb11.http.enable, OldConfig.http.enable) || !isEqual(NewOb11.http.host, OldConfig.http.host) || !isEqual(NewOb11.http.port, OldConfig.http.port);
      const isWsChanged = !isEqual(NewOb11.ws.enable, OldConfig.ws.enable) || !isEqual(NewOb11.ws.host, OldConfig.ws.host) || !isEqual(NewOb11.ws.port, OldConfig.ws.port);
      const isWsReverseChanged = !isEqual(NewOb11.reverseWs.enable, OldConfig.reverseWs.enable) || !isEqual(NewOb11.reverseWs.urls, OldConfig.reverseWs.urls);
      if (check_http_ws_equal(NewOb11) || check_http_ws_equal(OldConfig)) {
        if (isHttpChanged || isWsChanged) {
          log("http与ws进行热重载");
          ob11WebsocketServer.stop();
          ob11HTTPServer.stop();
          if (NewOb11.http.enable) {
            ob11HTTPServer.start(NewOb11.http.port, NewOb11.http.host);
          }
          if (NewOb11.ws.enable) {
            if (check_http_ws_equal(NewOb11) && ob11HTTPServer.server) {
              ob11WebsocketServer.start(ob11HTTPServer.server);
            } else {
              ob11WebsocketServer.start(NewOb11.ws.port, NewOb11.ws.host);
            }
          }
        }
      } else {
        if (isHttpChanged) {
          log("http进行热重载");
          ob11HTTPServer.stop();
          if (NewOb11.http.enable) {
            ob11HTTPServer.start(NewOb11.http.port, NewOb11.http.host);
          }
        }
        if (isWsChanged) {
          log("ws进行热重载");
          ob11WebsocketServer.stop();
          if (NewOb11.ws.enable) {
            ob11WebsocketServer.start(NewOb11.ws.port, NewOb11.ws.host);
          }
        }
      }
      if (isWsReverseChanged) {
        log("反向ws进行热重载");
        ob11ReverseWebsockets.stop();
        if (NewOb11.reverseWs.enable) {
          ob11ReverseWebsockets.start();
        }
      }
    } catch (e) {
      logError("热重载配置失败", e);
    }
  }
  async postGroupNotifies(notifies) {
    for (const notify of notifies) {
      try {
        notify.time = Date.now();
        const notifyTime = parseInt(notify.seq) / 1e3 / 1e3;
        if (notifyTime < this.bootTime) {
          continue;
        }
        const flag = notify.group.groupCode + "|" + notify.seq + "|" + notify.type;
        logDebug("收到群通知", notify);
        if ([GroupNotifyTypes.ADMIN_SET, GroupNotifyTypes.ADMIN_UNSET, GroupNotifyTypes.ADMIN_UNSET_OTHER].includes(notify.type)) {
          const member1 = await getGroupMember(notify.group.groupCode, notify.user1.uid);
          logDebug("有管理员变动通知");
          const groupAdminNoticeEvent = new OB11GroupAdminNoticeEvent();
          groupAdminNoticeEvent.group_id = parseInt(notify.group.groupCode);
          logDebug("开始获取变动的管理员");
          if (member1) {
            logDebug("变动管理员获取成功");
            groupAdminNoticeEvent.user_id = parseInt(member1.uin);
            groupAdminNoticeEvent.sub_type = [GroupNotifyTypes.ADMIN_UNSET, GroupNotifyTypes.ADMIN_UNSET_OTHER].includes(notify.type) ? "unset" : "set";
            postOB11Event(groupAdminNoticeEvent, true);
          } else {
            logDebug("获取群通知的成员信息失败", notify, getGroup(notify.group.groupCode));
          }
        } else if (notify.type == GroupNotifyTypes.MEMBER_EXIT || notify.type == GroupNotifyTypes.KICK_MEMBER) {
          logDebug("有成员退出通知", notify);
          try {
            const member1Uin = await NTQQUserApi.getUinByUid(notify.user1.uid);
            let operatorId = member1Uin;
            let subType = "leave";
            if (notify.user2.uid) {
              const member2Uin = await NTQQUserApi.getUinByUid(notify.user2.uid);
              if (member2Uin) {
                operatorId = member2Uin;
              }
              subType = "kick";
            }
            const groupDecreaseEvent = new OB11GroupDecreaseEvent(parseInt(notify.group.groupCode), parseInt(member1Uin), parseInt(operatorId), subType);
            postOB11Event(groupDecreaseEvent, true);
          } catch (e) {
            logError("获取群通知的成员信息失败", notify, e.stack.toString());
          }
        } else if ([GroupNotifyTypes.JOIN_REQUEST].includes(notify.type) && notify.status == 1) {
          logDebug("有加群请求");
          const groupRequestEvent = new OB11GroupRequestEvent();
          groupRequestEvent.group_id = parseInt(notify.group.groupCode);
          let requestQQ = "";
          try {
            requestQQ = await NTQQUserApi.getUinByUid(notify.user1.uid);
            if (isNaN(parseInt(requestQQ))) {
              requestQQ = (await NTQQUserApi.getUserDetailInfo(notify.user1.uid)).uin;
            }
          } catch (e) {
            logError("获取加群人QQ号失败 Uid:", notify.user1.uid, e);
          }
          groupRequestEvent.user_id = parseInt(requestQQ) || 0;
          groupRequestEvent.sub_type = "add";
          groupRequestEvent.comment = notify.postscript;
          groupRequestEvent.flag = flag;
          postOB11Event(groupRequestEvent);
        } else if (notify.type == GroupNotifyTypes.INVITE_ME) {
          logDebug(`收到邀请我加群通知:${notify}`);
          const groupInviteEvent = new OB11GroupRequestEvent();
          groupInviteEvent.group_id = parseInt(notify.group.groupCode);
          const user_id = await NTQQUserApi.getUinByUid(notify.user2.uid) || "";
          groupInviteEvent.user_id = parseInt(user_id);
          groupInviteEvent.sub_type = "invite";
          groupInviteEvent.flag = flag;
          postOB11Event(groupInviteEvent);
        }
      } catch (e) {
        logDebug("解析群通知失败", e.stack.toString());
      }
    }
  }
  async postRecallMsg(msgList) {
    for (const message of msgList) {
      if (message.recallTime != "0") {
        const oriMessageId = await MessageUnique.getShortIdByMsgId(message.msgId);
        if (!oriMessageId) {
          continue;
        }
        if (message.chatType == ChatType.friend) {
          const friendRecallEvent = new OB11FriendRecallNoticeEvent(parseInt(message.senderUin), oriMessageId);
          postOB11Event(friendRecallEvent);
        } else if (message.chatType == ChatType.group) {
          let operatorId = message.senderUin;
          for (const element of message.elements) {
            const operatorUid = element.grayTipElement?.revokeElement.operatorUid;
            const operator = await getGroupMember(message.peerUin, operatorUid);
            operatorId = operator?.uin || message.senderUin;
          }
          const groupRecallEvent = new OB11GroupRecallNoticeEvent(parseInt(message.peerUin), parseInt(message.senderUin), parseInt(operatorId), oriMessageId);
          postOB11Event(groupRecallEvent);
        }
      }
    }
  }
  async postFriendRequest(reqs) {
    for (const req of reqs) {
      if (!!req.isInitiator || req.isDecide && req.reqType !== BuddyReqType.KMEINITIATORWAITPEERCONFIRM) {
        continue;
      }
      const friendRequestEvent = new OB11FriendRequestEvent();
      try {
        const requesterUin = await NTQQUserApi.getUinByUid(req.friendUid);
        friendRequestEvent.user_id = parseInt(requesterUin);
      } catch (e) {
        logDebug("获取加好友者QQ号失败", e);
      }
      friendRequestEvent.flag = req.friendUid + "|" + req.reqTime;
      friendRequestEvent.comment = req.extWords;
      postOB11Event(friendRequestEvent);
    }
  }
  // async postGroupMemberChange(groupList: Group[]) {
  //   // todo: 有无更好的方法判断群成员变动
  //   const newGroupList = groupList;
  //   for (const group of newGroupList) {
  //     const existGroup = await getGroup(group.groupCode);
  //     if (existGroup) {
  //       if (existGroup.memberCount > group.memberCount) {
  //         log(`群(${group.groupCode})成员数量减少${existGroup.memberCount} -> ${group.memberCount}`);
  //         const oldMembers = existGroup.members;
  //         const newMembers = await NTQQGroupApi.getGroupMembers(group.groupCode);
  //         group.members = newMembers;
  //         const newMembersSet = new Set<string>();  // 建立索引降低时间复杂度
  //
  //         for (const member of newMembers) {
  //           newMembersSet.add(member.uin);
  //         }
  //
  //         // 判断bot是否是管理员，如果是管理员不需要从这里得知有人退群，这里的退群无法得知是主动退群还是被踢
  //         const bot = await getGroupMember(group.groupCode, selfInfo.uin);
  //         if (bot!.role == GroupMemberRole.admin || bot!.role == GroupMemberRole.owner) {
  //           continue;
  //         }
  //         for (const member of oldMembers) {
  //           if (!newMembersSet.has(member.uin) && member.uin != selfInfo.uin) {
  //             postOB11Event(new OB11GroupDecreaseEvent(parseInt(group.groupCode), parseInt(member.uin), parseInt(member.uin), 'leave'));
  //             break;
  //           }
  //         }
  //       }
  //     }
  //   }
  // }
}

function _defineProperty$3(e, r, t) {
  return (r = _toPropertyKey$3(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$3(t) {
  var i = _toPrimitive$3(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$3(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class Config extends ConfigBase {
  constructor() {
    super();
    _defineProperty$3(this, "name", "napcat");
    _defineProperty$3(this, "fileLog", true);
    _defineProperty$3(this, "consoleLog", true);
    _defineProperty$3(this, "fileLogLevel", LogLevel.DEBUG);
    _defineProperty$3(this, "consoleLogLevel", LogLevel.INFO);
  }
}
const napCatConfig = new Config();

function _defineProperty$2(e, r, t) {
  return (r = _toPropertyKey$2(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$2(t) {
  var i = _toPrimitive$2(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$2(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class NapCatCore {
  constructor() {
    _defineProperty$2(this, "session", void 0);
    _defineProperty$2(this, "util", void 0);
    _defineProperty$2(this, "engine", void 0);
    _defineProperty$2(this, "loginListener", void 0);
    _defineProperty$2(this, "loginService", void 0);
    _defineProperty$2(this, "onLoginSuccessFuncList", []);
    _defineProperty$2(this, "proxyHandler", {
      get(target, prop, receiver) {
        if (typeof target[prop] === "undefined") {
          return (...args) => {
            logDebug(`${target.constructor.name} has no method ${prop}`);
          };
        }
        return Reflect.get(target, prop, receiver);
      }
    });
    this.engine = new QQWrapper.NodeIQQNTWrapperEngine();
    this.util = new QQWrapper.NodeQQNTWrapperUtil();
    this.loginService = new QQWrapper.NodeIKernelLoginService();
    this.session = new QQWrapper.NodeIQQNTWrapperSession();
    this.loginListener = new LoginListener();
    this.loginListener.onUserLoggedIn = (userid) => {
      logError("当前账号(" + userid + ")已登录,无法重复登录");
    };
    this.initConfig();
    this.loginListener.onQRCodeLoginSucceed = (arg) => {
      this.initSession(arg.uin, arg.uid).then((r) => {
        selfInfo.uin = arg.uin;
        selfInfo.uid = arg.uid;
        napCatConfig.read();
        setLogLevel(napCatConfig.fileLogLevel, napCatConfig.consoleLogLevel);
        enableFileLog(napCatConfig.fileLog);
        enableConsoleLog(napCatConfig.consoleLog);
        setLogSelfInfo(selfInfo);
        const dataPath = path__default.resolve(this.dataPath, "./NapCat/data");
        fs__default.mkdirSync(dataPath, {
          recursive: true
        });
        logDebug("本账号数据/缓存目录：", dataPath);
        this.initDataListener();
        this.onLoginSuccessFuncList.map((cb) => {
          new Promise((resolve, reject) => {
            const result = cb(arg.uin, arg.uid);
            if (result instanceof Promise) {
              result.then(resolve).catch(reject);
            }
          }).then();
        });
      }).catch((e) => {
        logError("initSession failed", e);
        throw new Error(`启动失败: ${JSON.stringify(e)}`);
      });
    };
    this.loginListener.onQRCodeSessionFailed = (errType, errCode, errMsg) => {
      logError("登录失败(onQRCodeSessionFailed)", errMsg);
      this.loginService.getQRCodePicture();
    };
    this.loginListener.onLoginFailed = (args) => {
      logError("登录失败(onLoginFailed)", args);
    };
    this.loginListener = new Proxy(this.loginListener, this.proxyHandler);
    this.loginService.addKernelLoginListener(new QQWrapper.NodeIKernelLoginListener(this.loginListener));
  }
  get dataPath() {
    let result = this.util.getNTUserDataInfoConfig();
    if (!result) {
      result = path__default.resolve(os.homedir(), "./.config/QQ");
      fs__default.mkdirSync(result, {
        recursive: true
      });
    }
    return result;
  }
  get dataPathGlobal() {
    return path__default.resolve(this.dataPath, "./nt_qq/global");
  }
  initConfig() {
    this.engine.initWithDeskTopConfig({
      base_path_prefix: "",
      platform_type: 3,
      app_type: 4,
      app_version: getFullQQVesion(),
      os_version: "Windows 10 Pro",
      use_xlog: true,
      qua: QQVersionQua,
      global_path_config: {
        desktopGlobalPath: this.dataPathGlobal
      },
      thumb_config: {
        maxSide: 324,
        minSide: 48,
        longLimit: 6,
        density: 2
      }
    }, new QQWrapper.NodeIGlobalAdapter(new GlobalAdapter()));
    this.loginService.initConfig({
      machineId: "",
      appid: QQVersionAppid,
      platVer: systemVersion,
      commonPath: this.dataPathGlobal,
      clientVer: getFullQQVesion(),
      hostName: hostname
    });
  }
  initSession(uin, uid) {
    return new Promise(async (res, rej) => {
      const sessionConfig = await genSessionConfig(uin, uid, this.dataPath);
      const sessionListener = new SessionListener();
      sessionListener.onSessionInitComplete = (r) => {
        if (r === 0) {
          return res(0);
        }
        rej(r);
      };
      this.session.init(sessionConfig, new QQWrapper.NodeIDependsAdapter(new DependsAdapter()), new QQWrapper.NodeIDispatcherAdapter(new DispatcherAdapter()), new QQWrapper.NodeIKernelSessionListener(sessionListener));
      try {
        this.session.startNT(0);
      } catch (__) {
        try {
          this.session.startNT();
        } catch (e) {
          rej("init failed " + e);
        }
      }
    });
  }
  initDataListener() {
    const msgListener = new MsgListener();
    msgListener.onLineDev = (Devices) => {
      DeviceList.splice(0, DeviceList.length);
      Devices.map((Device) => {
        let DeviceData = {
          app_id: Device.devUid,
          device_name: Device.clientType.toString(),
          device_kind: Device.clientType.toString()
        };
        DeviceList.push(DeviceData);
      });
    };
    msgListener.onKickedOffLine = (Info) => {
      log("[KickedOffLine] [" + Info.tipsTitle + "] " + Info.tipsDesc);
    };
    msgListener.onAddSendMsg = (msg) => {
      stat.packet_sent += 1;
      stat.message_sent += 1;
      stat.last_message_time = Math.floor(Date.now() / 1e3);
    };
    msgListener.onRecvMsg = (msgList) => {
      stat.packet_received += 1;
      stat.message_received += msgList.length;
      stat.last_message_time = Math.floor(Date.now() / 1e3);
    };
    msgListener.onRecvSysMsg = (...args) => {
      stat.packet_received += 1;
    };
    this.addListener(msgListener);
    const buddyListener = new BuddyListener();
    this.addListener(buddyListener);
    if (!requireMinNTQQBuild("26702")) {
      this.session.getBuddyService().getBuddyList(true).then((arg) => {
      });
    }
    const profileListener = new ProfileListener();
    profileListener.onProfileDetailInfoChanged = (profile) => {
      if (profile.uid === selfInfo.uid) {
        Object.assign(selfInfo, profile);
      }
    };
    profileListener.onSelfStatusChanged = (Info) => {
    };
    this.addListener(profileListener);
    const groupListener = new GroupListener();
    groupListener.onGroupListUpdate = (updateType, groupList) => {
      groupList.map((g) => {
        const existGroup = groups.get(g.groupCode);
        if (existGroup && g.memberCount === existGroup.memberCount) {
          Object.assign(existGroup, g);
        } else {
          groups.set(g.groupCode, g);
        }
        const sceneId = this.session.getGroupService().createMemberListScene(g.groupCode, "groupMemberList_MainWindow");
        this.session.getGroupService().getNextMemberList(sceneId, void 0, 3e3).then((r) => {
        });
      });
    };
    groupListener.onMemberListChange = (arg) => {
      const groupCode = arg.sceneId.split("_")[0];
      if (groupMembers.has(groupCode)) {
        const existMembers = groupMembers.get(groupCode);
        arg.infos.forEach((member, uid) => {
          const existMember = existMembers.get(uid);
          if (existMember) {
            Object.assign(existMember, member);
          } else {
            existMembers.set(uid, member);
          }
          if (member.isDelete) {
            existMembers.delete(uid);
          }
        });
      } else {
        groupMembers.set(groupCode, arg.infos);
      }
    };
    groupListener.onMemberInfoChange = (groupCode, changeType, members) => {
      if (changeType === 0 && members.get(selfInfo.uid)?.isDelete) {
        setTimeout(() => {
          groups.delete(groupCode);
        }, 5e3);
      }
      const existMembers = groupMembers.get(groupCode);
      if (existMembers) {
        members.forEach((member, uid) => {
          const existMember = existMembers.get(uid);
          if (existMember) {
            member.isChangeRole = this.checkAdminEvent(groupCode, member, existMember);
            Object.assign(existMember, member);
          } else {
            existMembers.set(uid, member);
          }
          if (member.isDelete) {
            existMembers.delete(uid);
          }
        });
      } else {
        groupMembers.set(groupCode, members);
      }
    };
    this.addListener(groupListener);
  }
  addListener(listener) {
    listener = new Proxy(listener, this.proxyHandler);
    switch (listener.constructor.name) {
      case "BuddyListener": {
        return this.session.getBuddyService().addKernelBuddyListener(new QQWrapper.NodeIKernelBuddyListener(listener));
      }
      case "GroupListener": {
        return this.session.getGroupService().addKernelGroupListener(new QQWrapper.NodeIKernelGroupListener(listener));
      }
      case "MsgListener": {
        return this.session.getMsgService().addKernelMsgListener(new QQWrapper.NodeIKernelMsgListener(listener));
      }
      case "ProfileListener": {
        return this.session.getProfileService().addKernelProfileListener(new QQWrapper.NodeIKernelProfileListener(listener));
      }
      default:
        return -1;
    }
  }
  onLoginSuccess(func) {
    NTEventDispatch.init({
      ListenerMap: QQWrapper,
      WrapperSession: this.session
    });
    this.onLoginSuccessFuncList.push(func);
  }
  async quickLogin(uin) {
    const loginList = await this.loginService.getLoginList();
    if (loginList.result !== 0) throw new Error("没有可快速登录的QQ号");
    const currentLogin = loginList.LocalLoginInfoList.find((item) => item.uin === uin);
    if (!currentLogin || !currentLogin?.isQuickLogin) throw new Error(`${uin}快速登录不可用`);
    await sleep(1e3);
    const loginRet = await this.loginService.quickLoginWithUin(uin);
    if (!loginRet.result) {
      throw new Error("快速登录失败 " + loginRet.loginErrorInfo.errMsg);
    }
    return loginRet;
  }
  async qrLogin(cb) {
    return new Promise((resolve, reject) => {
      this.loginListener.onQRCodeGetPicture = (arg) => {
        const base64Data = arg.pngBase64QrcodeData.split("data:image/png;base64,")[1];
        const buffer = Buffer.from(base64Data, "base64");
        cb(arg.qrcodeUrl, arg.pngBase64QrcodeData, buffer);
      };
      this.loginService.getQRCodePicture();
    });
  }
  async passwordLogin(uin, password, proofSig, proofRand, proofSid) {
    const passwordMd5 = crypto$1.createHash("md5").update(password).digest("hex");
    const loginArg = {
      uin,
      passwordMd5,
      step: proofSig && proofRand && proofSid ? 1 : 0,
      newDeviceLoginSig: "",
      proofWaterSig: proofSig || "",
      proofWaterRand: proofRand || "",
      proofWaterSid: proofSid || ""
    };
    await this.loginService.getLoginList();
    await sleep(1e3);
    const ret = await this.loginService.passwordLogin(loginArg);
    switch (ret.result) {
          }
  }
  async getQuickLoginList() {
    const loginList = await this.loginService.getLoginList();
    return loginList;
  }
  checkAdminEvent(groupCode, memberNew, memberOld) {
    if (memberNew.role !== memberOld?.role) {
      log(`群 ${groupCode} ${memberNew.nick} 角色变更为 ${memberNew.role === 3 ? "管理员" : "群员"}`);
      return true;
    }
    return false;
  }
}
const napCatCore = new NapCatCore();

var commander = {};

var argument = {};

var error = {};

/**
 * CommanderError class
 */

let CommanderError$3 = class CommanderError extends Error {
  /**
   * Constructs the CommanderError class
   * @param {number} exitCode suggested exit code which could be used with process.exit
   * @param {string} code an id string representing the error
   * @param {string} message human-readable description of the error
   */
  constructor(exitCode, code, message) {
    super(message);
    // properly capture stack trace in Node.js
    Error.captureStackTrace(this, this.constructor);
    this.name = this.constructor.name;
    this.code = code;
    this.exitCode = exitCode;
    this.nestedError = undefined;
  }
};

/**
 * InvalidArgumentError class
 */
let InvalidArgumentError$4 = class InvalidArgumentError extends CommanderError$3 {
  /**
   * Constructs the InvalidArgumentError class
   * @param {string} [message] explanation of why argument is invalid
   */
  constructor(message) {
    super(1, 'commander.invalidArgument', message);
    // properly capture stack trace in Node.js
    Error.captureStackTrace(this, this.constructor);
    this.name = this.constructor.name;
  }
};
error.CommanderError = CommanderError$3;
error.InvalidArgumentError = InvalidArgumentError$4;

const {
  InvalidArgumentError: InvalidArgumentError$3
} = error;
let Argument$3 = class Argument {
  /**
   * Initialize a new command argument with the given name and description.
   * The default is that the argument is required, and you can explicitly
   * indicate this with <> around the name. Put [] around the name for an optional argument.
   *
   * @param {string} name
   * @param {string} [description]
   */

  constructor(name, description) {
    this.description = description || '';
    this.variadic = false;
    this.parseArg = undefined;
    this.defaultValue = undefined;
    this.defaultValueDescription = undefined;
    this.argChoices = undefined;
    switch (name[0]) {
      case '<':
        // e.g. <required>
        this.required = true;
        this._name = name.slice(1, -1);
        break;
      case '[':
        // e.g. [optional]
        this.required = false;
        this._name = name.slice(1, -1);
        break;
      default:
        this.required = true;
        this._name = name;
        break;
    }
    if (this._name.length > 3 && this._name.slice(-3) === '...') {
      this.variadic = true;
      this._name = this._name.slice(0, -3);
    }
  }

  /**
   * Return argument name.
   *
   * @return {string}
   */

  name() {
    return this._name;
  }

  /**
   * @package
   */

  _concatValue(value, previous) {
    if (previous === this.defaultValue || !Array.isArray(previous)) {
      return [value];
    }
    return previous.concat(value);
  }

  /**
   * Set the default value, and optionally supply the description to be displayed in the help.
   *
   * @param {*} value
   * @param {string} [description]
   * @return {Argument}
   */

  default(value, description) {
    this.defaultValue = value;
    this.defaultValueDescription = description;
    return this;
  }

  /**
   * Set the custom handler for processing CLI command arguments into argument values.
   *
   * @param {Function} [fn]
   * @return {Argument}
   */

  argParser(fn) {
    this.parseArg = fn;
    return this;
  }

  /**
   * Only allow argument value to be one of choices.
   *
   * @param {string[]} values
   * @return {Argument}
   */

  choices(values) {
    this.argChoices = values.slice();
    this.parseArg = (arg, previous) => {
      if (!this.argChoices.includes(arg)) {
        throw new InvalidArgumentError$3(`Allowed choices are ${this.argChoices.join(', ')}.`);
      }
      if (this.variadic) {
        return this._concatValue(arg, previous);
      }
      return arg;
    };
    return this;
  }

  /**
   * Make argument required.
   *
   * @returns {Argument}
   */
  argRequired() {
    this.required = true;
    return this;
  }

  /**
   * Make argument optional.
   *
   * @returns {Argument}
   */
  argOptional() {
    this.required = false;
    return this;
  }
};

/**
 * Takes an argument and returns its human readable equivalent for help usage.
 *
 * @param {Argument} arg
 * @return {string}
 * @private
 */

function humanReadableArgName$2(arg) {
  const nameOutput = arg.name() + (arg.variadic === true ? '...' : '');
  return arg.required ? '<' + nameOutput + '>' : '[' + nameOutput + ']';
}
argument.Argument = Argument$3;
argument.humanReadableArgName = humanReadableArgName$2;

var command = {};

var help = {};

const {
  humanReadableArgName: humanReadableArgName$1
} = argument;

/**
 * TypeScript import types for JSDoc, used by Visual Studio Code IntelliSense and `npm run typescript-checkJS`
 * https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html#import-types
 * @typedef { import("./argument.js").Argument } Argument
 * @typedef { import("./command.js").Command } Command
 * @typedef { import("./option.js").Option } Option
 */

// Although this is a class, methods are static in style to allow override using subclass or just functions.
let Help$3 = class Help {
  constructor() {
    this.helpWidth = undefined;
    this.sortSubcommands = false;
    this.sortOptions = false;
    this.showGlobalOptions = false;
  }

  /**
   * Get an array of the visible subcommands. Includes a placeholder for the implicit help command, if there is one.
   *
   * @param {Command} cmd
   * @returns {Command[]}
   */

  visibleCommands(cmd) {
    const visibleCommands = cmd.commands.filter(cmd => !cmd._hidden);
    const helpCommand = cmd._getHelpCommand();
    if (helpCommand && !helpCommand._hidden) {
      visibleCommands.push(helpCommand);
    }
    if (this.sortSubcommands) {
      visibleCommands.sort((a, b) => {
        // @ts-ignore: because overloaded return type
        return a.name().localeCompare(b.name());
      });
    }
    return visibleCommands;
  }

  /**
   * Compare options for sort.
   *
   * @param {Option} a
   * @param {Option} b
   * @returns {number}
   */
  compareOptions(a, b) {
    const getSortKey = option => {
      // WYSIWYG for order displayed in help. Short used for comparison if present. No special handling for negated.
      return option.short ? option.short.replace(/^-/, '') : option.long.replace(/^--/, '');
    };
    return getSortKey(a).localeCompare(getSortKey(b));
  }

  /**
   * Get an array of the visible options. Includes a placeholder for the implicit help option, if there is one.
   *
   * @param {Command} cmd
   * @returns {Option[]}
   */

  visibleOptions(cmd) {
    const visibleOptions = cmd.options.filter(option => !option.hidden);
    // Built-in help option.
    const helpOption = cmd._getHelpOption();
    if (helpOption && !helpOption.hidden) {
      // Automatically hide conflicting flags. Bit dubious but a historical behaviour that is convenient for single-command programs.
      const removeShort = helpOption.short && cmd._findOption(helpOption.short);
      const removeLong = helpOption.long && cmd._findOption(helpOption.long);
      if (!removeShort && !removeLong) {
        visibleOptions.push(helpOption); // no changes needed
      } else if (helpOption.long && !removeLong) {
        visibleOptions.push(cmd.createOption(helpOption.long, helpOption.description));
      } else if (helpOption.short && !removeShort) {
        visibleOptions.push(cmd.createOption(helpOption.short, helpOption.description));
      }
    }
    if (this.sortOptions) {
      visibleOptions.sort(this.compareOptions);
    }
    return visibleOptions;
  }

  /**
   * Get an array of the visible global options. (Not including help.)
   *
   * @param {Command} cmd
   * @returns {Option[]}
   */

  visibleGlobalOptions(cmd) {
    if (!this.showGlobalOptions) return [];
    const globalOptions = [];
    for (let ancestorCmd = cmd.parent; ancestorCmd; ancestorCmd = ancestorCmd.parent) {
      const visibleOptions = ancestorCmd.options.filter(option => !option.hidden);
      globalOptions.push(...visibleOptions);
    }
    if (this.sortOptions) {
      globalOptions.sort(this.compareOptions);
    }
    return globalOptions;
  }

  /**
   * Get an array of the arguments if any have a description.
   *
   * @param {Command} cmd
   * @returns {Argument[]}
   */

  visibleArguments(cmd) {
    // Side effect! Apply the legacy descriptions before the arguments are displayed.
    if (cmd._argsDescription) {
      cmd.registeredArguments.forEach(argument => {
        argument.description = argument.description || cmd._argsDescription[argument.name()] || '';
      });
    }

    // If there are any arguments with a description then return all the arguments.
    if (cmd.registeredArguments.find(argument => argument.description)) {
      return cmd.registeredArguments;
    }
    return [];
  }

  /**
   * Get the command term to show in the list of subcommands.
   *
   * @param {Command} cmd
   * @returns {string}
   */

  subcommandTerm(cmd) {
    // Legacy. Ignores custom usage string, and nested commands.
    const args = cmd.registeredArguments.map(arg => humanReadableArgName$1(arg)).join(' ');
    return cmd._name + (cmd._aliases[0] ? '|' + cmd._aliases[0] : '') + (cmd.options.length ? ' [options]' : '') + (
    // simplistic check for non-help option
    args ? ' ' + args : '');
  }

  /**
   * Get the option term to show in the list of options.
   *
   * @param {Option} option
   * @returns {string}
   */

  optionTerm(option) {
    return option.flags;
  }

  /**
   * Get the argument term to show in the list of arguments.
   *
   * @param {Argument} argument
   * @returns {string}
   */

  argumentTerm(argument) {
    return argument.name();
  }

  /**
   * Get the longest command term length.
   *
   * @param {Command} cmd
   * @param {Help} helper
   * @returns {number}
   */

  longestSubcommandTermLength(cmd, helper) {
    return helper.visibleCommands(cmd).reduce((max, command) => {
      return Math.max(max, helper.subcommandTerm(command).length);
    }, 0);
  }

  /**
   * Get the longest option term length.
   *
   * @param {Command} cmd
   * @param {Help} helper
   * @returns {number}
   */

  longestOptionTermLength(cmd, helper) {
    return helper.visibleOptions(cmd).reduce((max, option) => {
      return Math.max(max, helper.optionTerm(option).length);
    }, 0);
  }

  /**
   * Get the longest global option term length.
   *
   * @param {Command} cmd
   * @param {Help} helper
   * @returns {number}
   */

  longestGlobalOptionTermLength(cmd, helper) {
    return helper.visibleGlobalOptions(cmd).reduce((max, option) => {
      return Math.max(max, helper.optionTerm(option).length);
    }, 0);
  }

  /**
   * Get the longest argument term length.
   *
   * @param {Command} cmd
   * @param {Help} helper
   * @returns {number}
   */

  longestArgumentTermLength(cmd, helper) {
    return helper.visibleArguments(cmd).reduce((max, argument) => {
      return Math.max(max, helper.argumentTerm(argument).length);
    }, 0);
  }

  /**
   * Get the command usage to be displayed at the top of the built-in help.
   *
   * @param {Command} cmd
   * @returns {string}
   */

  commandUsage(cmd) {
    // Usage
    let cmdName = cmd._name;
    if (cmd._aliases[0]) {
      cmdName = cmdName + '|' + cmd._aliases[0];
    }
    let ancestorCmdNames = '';
    for (let ancestorCmd = cmd.parent; ancestorCmd; ancestorCmd = ancestorCmd.parent) {
      ancestorCmdNames = ancestorCmd.name() + ' ' + ancestorCmdNames;
    }
    return ancestorCmdNames + cmdName + ' ' + cmd.usage();
  }

  /**
   * Get the description for the command.
   *
   * @param {Command} cmd
   * @returns {string}
   */

  commandDescription(cmd) {
    // @ts-ignore: because overloaded return type
    return cmd.description();
  }

  /**
   * Get the subcommand summary to show in the list of subcommands.
   * (Fallback to description for backwards compatibility.)
   *
   * @param {Command} cmd
   * @returns {string}
   */

  subcommandDescription(cmd) {
    // @ts-ignore: because overloaded return type
    return cmd.summary() || cmd.description();
  }

  /**
   * Get the option description to show in the list of options.
   *
   * @param {Option} option
   * @return {string}
   */

  optionDescription(option) {
    const extraInfo = [];
    if (option.argChoices) {
      extraInfo.push(
      // use stringify to match the display of the default value
      `choices: ${option.argChoices.map(choice => JSON.stringify(choice)).join(', ')}`);
    }
    if (option.defaultValue !== undefined) {
      // default for boolean and negated more for programmer than end user,
      // but show true/false for boolean option as may be for hand-rolled env or config processing.
      const showDefault = option.required || option.optional || option.isBoolean() && typeof option.defaultValue === 'boolean';
      if (showDefault) {
        extraInfo.push(`default: ${option.defaultValueDescription || JSON.stringify(option.defaultValue)}`);
      }
    }
    // preset for boolean and negated are more for programmer than end user
    if (option.presetArg !== undefined && option.optional) {
      extraInfo.push(`preset: ${JSON.stringify(option.presetArg)}`);
    }
    if (option.envVar !== undefined) {
      extraInfo.push(`env: ${option.envVar}`);
    }
    if (extraInfo.length > 0) {
      return `${option.description} (${extraInfo.join(', ')})`;
    }
    return option.description;
  }

  /**
   * Get the argument description to show in the list of arguments.
   *
   * @param {Argument} argument
   * @return {string}
   */

  argumentDescription(argument) {
    const extraInfo = [];
    if (argument.argChoices) {
      extraInfo.push(
      // use stringify to match the display of the default value
      `choices: ${argument.argChoices.map(choice => JSON.stringify(choice)).join(', ')}`);
    }
    if (argument.defaultValue !== undefined) {
      extraInfo.push(`default: ${argument.defaultValueDescription || JSON.stringify(argument.defaultValue)}`);
    }
    if (extraInfo.length > 0) {
      const extraDescripton = `(${extraInfo.join(', ')})`;
      if (argument.description) {
        return `${argument.description} ${extraDescripton}`;
      }
      return extraDescripton;
    }
    return argument.description;
  }

  /**
   * Generate the built-in help text.
   *
   * @param {Command} cmd
   * @param {Help} helper
   * @returns {string}
   */

  formatHelp(cmd, helper) {
    const termWidth = helper.padWidth(cmd, helper);
    const helpWidth = helper.helpWidth || 80;
    const itemIndentWidth = 2;
    const itemSeparatorWidth = 2; // between term and description
    function formatItem(term, description) {
      if (description) {
        const fullText = `${term.padEnd(termWidth + itemSeparatorWidth)}${description}`;
        return helper.wrap(fullText, helpWidth - itemIndentWidth, termWidth + itemSeparatorWidth);
      }
      return term;
    }
    function formatList(textArray) {
      return textArray.join('\n').replace(/^/gm, ' '.repeat(itemIndentWidth));
    }

    // Usage
    let output = [`Usage: ${helper.commandUsage(cmd)}`, ''];

    // Description
    const commandDescription = helper.commandDescription(cmd);
    if (commandDescription.length > 0) {
      output = output.concat([helper.wrap(commandDescription, helpWidth, 0), '']);
    }

    // Arguments
    const argumentList = helper.visibleArguments(cmd).map(argument => {
      return formatItem(helper.argumentTerm(argument), helper.argumentDescription(argument));
    });
    if (argumentList.length > 0) {
      output = output.concat(['Arguments:', formatList(argumentList), '']);
    }

    // Options
    const optionList = helper.visibleOptions(cmd).map(option => {
      return formatItem(helper.optionTerm(option), helper.optionDescription(option));
    });
    if (optionList.length > 0) {
      output = output.concat(['Options:', formatList(optionList), '']);
    }
    if (this.showGlobalOptions) {
      const globalOptionList = helper.visibleGlobalOptions(cmd).map(option => {
        return formatItem(helper.optionTerm(option), helper.optionDescription(option));
      });
      if (globalOptionList.length > 0) {
        output = output.concat(['Global Options:', formatList(globalOptionList), '']);
      }
    }

    // Commands
    const commandList = helper.visibleCommands(cmd).map(cmd => {
      return formatItem(helper.subcommandTerm(cmd), helper.subcommandDescription(cmd));
    });
    if (commandList.length > 0) {
      output = output.concat(['Commands:', formatList(commandList), '']);
    }
    return output.join('\n');
  }

  /**
   * Calculate the pad width from the maximum term length.
   *
   * @param {Command} cmd
   * @param {Help} helper
   * @returns {number}
   */

  padWidth(cmd, helper) {
    return Math.max(helper.longestOptionTermLength(cmd, helper), helper.longestGlobalOptionTermLength(cmd, helper), helper.longestSubcommandTermLength(cmd, helper), helper.longestArgumentTermLength(cmd, helper));
  }

  /**
   * Wrap the given string to width characters per line, with lines after the first indented.
   * Do not wrap if insufficient room for wrapping (minColumnWidth), or string is manually formatted.
   *
   * @param {string} str
   * @param {number} width
   * @param {number} indent
   * @param {number} [minColumnWidth=40]
   * @return {string}
   *
   */

  wrap(str, width, indent, minColumnWidth = 40) {
    // Full \s characters, minus the linefeeds.
    const indents = ' \\f\\t\\v\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000\ufeff';
    // Detect manually wrapped and indented strings by searching for line break followed by spaces.
    const manualIndent = new RegExp(`[\\n][${indents}]+`);
    if (str.match(manualIndent)) return str;
    // Do not wrap if not enough room for a wrapped column of text (as could end up with a word per line).
    const columnWidth = width - indent;
    if (columnWidth < minColumnWidth) return str;
    const leadingStr = str.slice(0, indent);
    const columnText = str.slice(indent).replace('\r\n', '\n');
    const indentString = ' '.repeat(indent);
    const zeroWidthSpace = '\u200B';
    const breaks = `\\s${zeroWidthSpace}`;
    // Match line end (so empty lines don't collapse),
    // or as much text as will fit in column, or excess text up to first break.
    const regex = new RegExp(`\n|.{1,${columnWidth - 1}}([${breaks}]|$)|[^${breaks}]+?([${breaks}]|$)`, 'g');
    const lines = columnText.match(regex) || [];
    return leadingStr + lines.map((line, i) => {
      if (line === '\n') return ''; // preserve empty lines
      return (i > 0 ? indentString : '') + line.trimEnd();
    }).join('\n');
  }
};
help.Help = Help$3;

var option = {};

const {
  InvalidArgumentError: InvalidArgumentError$2
} = error;
let Option$3 = class Option {
  /**
   * Initialize a new `Option` with the given `flags` and `description`.
   *
   * @param {string} flags
   * @param {string} [description]
   */

  constructor(flags, description) {
    this.flags = flags;
    this.description = description || '';
    this.required = flags.includes('<'); // A value must be supplied when the option is specified.
    this.optional = flags.includes('['); // A value is optional when the option is specified.
    // variadic test ignores <value,...> et al which might be used to describe custom splitting of single argument
    this.variadic = /\w\.\.\.[>\]]$/.test(flags); // The option can take multiple values.
    this.mandatory = false; // The option must have a value after parsing, which usually means it must be specified on command line.
    const optionFlags = splitOptionFlags(flags);
    this.short = optionFlags.shortFlag;
    this.long = optionFlags.longFlag;
    this.negate = false;
    if (this.long) {
      this.negate = this.long.startsWith('--no-');
    }
    this.defaultValue = undefined;
    this.defaultValueDescription = undefined;
    this.presetArg = undefined;
    this.envVar = undefined;
    this.parseArg = undefined;
    this.hidden = false;
    this.argChoices = undefined;
    this.conflictsWith = [];
    this.implied = undefined;
  }

  /**
   * Set the default value, and optionally supply the description to be displayed in the help.
   *
   * @param {*} value
   * @param {string} [description]
   * @return {Option}
   */

  default(value, description) {
    this.defaultValue = value;
    this.defaultValueDescription = description;
    return this;
  }

  /**
   * Preset to use when option used without option-argument, especially optional but also boolean and negated.
   * The custom processing (parseArg) is called.
   *
   * @example
   * new Option('--color').default('GREYSCALE').preset('RGB');
   * new Option('--donate [amount]').preset('20').argParser(parseFloat);
   *
   * @param {*} arg
   * @return {Option}
   */

  preset(arg) {
    this.presetArg = arg;
    return this;
  }

  /**
   * Add option name(s) that conflict with this option.
   * An error will be displayed if conflicting options are found during parsing.
   *
   * @example
   * new Option('--rgb').conflicts('cmyk');
   * new Option('--js').conflicts(['ts', 'jsx']);
   *
   * @param {(string | string[])} names
   * @return {Option}
   */

  conflicts(names) {
    this.conflictsWith = this.conflictsWith.concat(names);
    return this;
  }

  /**
   * Specify implied option values for when this option is set and the implied options are not.
   *
   * The custom processing (parseArg) is not called on the implied values.
   *
   * @example
   * program
   *   .addOption(new Option('--log', 'write logging information to file'))
   *   .addOption(new Option('--trace', 'log extra details').implies({ log: 'trace.txt' }));
   *
   * @param {object} impliedOptionValues
   * @return {Option}
   */
  implies(impliedOptionValues) {
    let newImplied = impliedOptionValues;
    if (typeof impliedOptionValues === 'string') {
      // string is not documented, but easy mistake and we can do what user probably intended.
      newImplied = {
        [impliedOptionValues]: true
      };
    }
    this.implied = Object.assign(this.implied || {}, newImplied);
    return this;
  }

  /**
   * Set environment variable to check for option value.
   *
   * An environment variable is only used if when processed the current option value is
   * undefined, or the source of the current value is 'default' or 'config' or 'env'.
   *
   * @param {string} name
   * @return {Option}
   */

  env(name) {
    this.envVar = name;
    return this;
  }

  /**
   * Set the custom handler for processing CLI option arguments into option values.
   *
   * @param {Function} [fn]
   * @return {Option}
   */

  argParser(fn) {
    this.parseArg = fn;
    return this;
  }

  /**
   * Whether the option is mandatory and must have a value after parsing.
   *
   * @param {boolean} [mandatory=true]
   * @return {Option}
   */

  makeOptionMandatory(mandatory = true) {
    this.mandatory = !!mandatory;
    return this;
  }

  /**
   * Hide option in help.
   *
   * @param {boolean} [hide=true]
   * @return {Option}
   */

  hideHelp(hide = true) {
    this.hidden = !!hide;
    return this;
  }

  /**
   * @package
   */

  _concatValue(value, previous) {
    if (previous === this.defaultValue || !Array.isArray(previous)) {
      return [value];
    }
    return previous.concat(value);
  }

  /**
   * Only allow option value to be one of choices.
   *
   * @param {string[]} values
   * @return {Option}
   */

  choices(values) {
    this.argChoices = values.slice();
    this.parseArg = (arg, previous) => {
      if (!this.argChoices.includes(arg)) {
        throw new InvalidArgumentError$2(`Allowed choices are ${this.argChoices.join(', ')}.`);
      }
      if (this.variadic) {
        return this._concatValue(arg, previous);
      }
      return arg;
    };
    return this;
  }

  /**
   * Return option name.
   *
   * @return {string}
   */

  name() {
    if (this.long) {
      return this.long.replace(/^--/, '');
    }
    return this.short.replace(/^-/, '');
  }

  /**
   * Return option name, in a camelcase format that can be used
   * as a object attribute key.
   *
   * @return {string}
   */

  attributeName() {
    return camelcase(this.name().replace(/^no-/, ''));
  }

  /**
   * Check if `arg` matches the short or long flag.
   *
   * @param {string} arg
   * @return {boolean}
   * @package
   */

  is(arg) {
    return this.short === arg || this.long === arg;
  }

  /**
   * Return whether a boolean option.
   *
   * Options are one of boolean, negated, required argument, or optional argument.
   *
   * @return {boolean}
   * @package
   */

  isBoolean() {
    return !this.required && !this.optional && !this.negate;
  }
};

/**
 * This class is to make it easier to work with dual options, without changing the existing
 * implementation. We support separate dual options for separate positive and negative options,
 * like `--build` and `--no-build`, which share a single option value. This works nicely for some
 * use cases, but is tricky for others where we want separate behaviours despite
 * the single shared option value.
 */
let DualOptions$1 = class DualOptions {
  /**
   * @param {Option[]} options
   */
  constructor(options) {
    this.positiveOptions = new Map();
    this.negativeOptions = new Map();
    this.dualOptions = new Set();
    options.forEach(option => {
      if (option.negate) {
        this.negativeOptions.set(option.attributeName(), option);
      } else {
        this.positiveOptions.set(option.attributeName(), option);
      }
    });
    this.negativeOptions.forEach((value, key) => {
      if (this.positiveOptions.has(key)) {
        this.dualOptions.add(key);
      }
    });
  }

  /**
   * Did the value come from the option, and not from possible matching dual option?
   *
   * @param {*} value
   * @param {Option} option
   * @returns {boolean}
   */
  valueFromOption(value, option) {
    const optionKey = option.attributeName();
    if (!this.dualOptions.has(optionKey)) return true;

    // Use the value to deduce if (probably) came from the option.
    const preset = this.negativeOptions.get(optionKey).presetArg;
    const negativeValue = preset !== undefined ? preset : false;
    return option.negate === (negativeValue === value);
  }
};

/**
 * Convert string from kebab-case to camelCase.
 *
 * @param {string} str
 * @return {string}
 * @private
 */

function camelcase(str) {
  return str.split('-').reduce((str, word) => {
    return str + word[0].toUpperCase() + word.slice(1);
  });
}

/**
 * Split the short and long flag out of something like '-m,--mixed <value>'
 *
 * @private
 */

function splitOptionFlags(flags) {
  let shortFlag;
  let longFlag;
  // Use original very loose parsing to maintain backwards compatibility for now,
  // which allowed for example unintended `-sw, --short-word` [sic].
  const flagParts = flags.split(/[ |,]+/);
  if (flagParts.length > 1 && !/^[[<]/.test(flagParts[1])) shortFlag = flagParts.shift();
  longFlag = flagParts.shift();
  // Add support for lone short flag without significantly changing parsing!
  if (!shortFlag && /^-[^-]$/.test(longFlag)) {
    shortFlag = longFlag;
    longFlag = undefined;
  }
  return {
    shortFlag,
    longFlag
  };
}
option.Option = Option$3;
option.DualOptions = DualOptions$1;

var suggestSimilar$2 = {};

const maxDistance = 3;
function editDistance(a, b) {
  // https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance
  // Calculating optimal string alignment distance, no substring is edited more than once.
  // (Simple implementation.)

  // Quick early exit, return worst case.
  if (Math.abs(a.length - b.length) > maxDistance) return Math.max(a.length, b.length);

  // distance between prefix substrings of a and b
  const d = [];

  // pure deletions turn a into empty string
  for (let i = 0; i <= a.length; i++) {
    d[i] = [i];
  }
  // pure insertions turn empty string into b
  for (let j = 0; j <= b.length; j++) {
    d[0][j] = j;
  }

  // fill matrix
  for (let j = 1; j <= b.length; j++) {
    for (let i = 1; i <= a.length; i++) {
      let cost = 1;
      if (a[i - 1] === b[j - 1]) {
        cost = 0;
      } else {
        cost = 1;
      }
      d[i][j] = Math.min(d[i - 1][j] + 1,
      // deletion
      d[i][j - 1] + 1,
      // insertion
      d[i - 1][j - 1] + cost // substitution
      );
      // transposition
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
      }
    }
  }
  return d[a.length][b.length];
}

/**
 * Find close matches, restricted to same number of edits.
 *
 * @param {string} word
 * @param {string[]} candidates
 * @returns {string}
 */

function suggestSimilar$1(word, candidates) {
  if (!candidates || candidates.length === 0) return '';
  // remove possible duplicates
  candidates = Array.from(new Set(candidates));
  const searchingOptions = word.startsWith('--');
  if (searchingOptions) {
    word = word.slice(2);
    candidates = candidates.map(candidate => candidate.slice(2));
  }
  let similar = [];
  let bestDistance = maxDistance;
  const minSimilarity = 0.4;
  candidates.forEach(candidate => {
    if (candidate.length <= 1) return; // no one character guesses

    const distance = editDistance(word, candidate);
    const length = Math.max(word.length, candidate.length);
    const similarity = (length - distance) / length;
    if (similarity > minSimilarity) {
      if (distance < bestDistance) {
        // better edit distance, throw away previous worse matches
        bestDistance = distance;
        similar = [candidate];
      } else if (distance === bestDistance) {
        similar.push(candidate);
      }
    }
  });
  similar.sort((a, b) => a.localeCompare(b));
  if (searchingOptions) {
    similar = similar.map(candidate => `--${candidate}`);
  }
  if (similar.length > 1) {
    return `\n(Did you mean one of ${similar.join(', ')}?)`;
  }
  if (similar.length === 1) {
    return `\n(Did you mean ${similar[0]}?)`;
  }
  return '';
}
suggestSimilar$2.suggestSimilar = suggestSimilar$1;

const EventEmitter = require$$0.EventEmitter;
const childProcess = require$$1$1;
const path = path__default;
const fs = fs__default;
const process$1 = process$2;
const {
  Argument: Argument$2,
  humanReadableArgName
} = argument;
const {
  CommanderError: CommanderError$2
} = error;
const {
  Help: Help$2
} = help;
const {
  Option: Option$2,
  DualOptions
} = option;
const {
  suggestSimilar
} = suggestSimilar$2;
let Command$2 = class Command extends EventEmitter {
  /**
   * Initialize a new `Command`.
   *
   * @param {string} [name]
   */

  constructor(name) {
    super();
    /** @type {Command[]} */
    this.commands = [];
    /** @type {Option[]} */
    this.options = [];
    this.parent = null;
    this._allowUnknownOption = false;
    this._allowExcessArguments = true;
    /** @type {Argument[]} */
    this.registeredArguments = [];
    this._args = this.registeredArguments; // deprecated old name
    /** @type {string[]} */
    this.args = []; // cli args with options removed
    this.rawArgs = [];
    this.processedArgs = []; // like .args but after custom processing and collecting variadic
    this._scriptPath = null;
    this._name = name || '';
    this._optionValues = {};
    this._optionValueSources = {}; // default, env, cli etc
    this._storeOptionsAsProperties = false;
    this._actionHandler = null;
    this._executableHandler = false;
    this._executableFile = null; // custom name for executable
    this._executableDir = null; // custom search directory for subcommands
    this._defaultCommandName = null;
    this._exitCallback = null;
    this._aliases = [];
    this._combineFlagAndOptionalValue = true;
    this._description = '';
    this._summary = '';
    this._argsDescription = undefined; // legacy
    this._enablePositionalOptions = false;
    this._passThroughOptions = false;
    this._lifeCycleHooks = {}; // a hash of arrays
    /** @type {(boolean | string)} */
    this._showHelpAfterError = false;
    this._showSuggestionAfterError = true;

    // see .configureOutput() for docs
    this._outputConfiguration = {
      writeOut: str => process$1.stdout.write(str),
      writeErr: str => process$1.stderr.write(str),
      getOutHelpWidth: () => process$1.stdout.isTTY ? process$1.stdout.columns : undefined,
      getErrHelpWidth: () => process$1.stderr.isTTY ? process$1.stderr.columns : undefined,
      outputError: (str, write) => write(str)
    };
    this._hidden = false;
    /** @type {(Option | null | undefined)} */
    this._helpOption = undefined; // Lazy created on demand. May be null if help option is disabled.
    this._addImplicitHelpCommand = undefined; // undecided whether true or false yet, not inherited
    /** @type {Command} */
    this._helpCommand = undefined; // lazy initialised, inherited
    this._helpConfiguration = {};
  }

  /**
   * Copy settings that are useful to have in common across root command and subcommands.
   *
   * (Used internally when adding a command using `.command()` so subcommands inherit parent settings.)
   *
   * @param {Command} sourceCommand
   * @return {Command} `this` command for chaining
   */
  copyInheritedSettings(sourceCommand) {
    this._outputConfiguration = sourceCommand._outputConfiguration;
    this._helpOption = sourceCommand._helpOption;
    this._helpCommand = sourceCommand._helpCommand;
    this._helpConfiguration = sourceCommand._helpConfiguration;
    this._exitCallback = sourceCommand._exitCallback;
    this._storeOptionsAsProperties = sourceCommand._storeOptionsAsProperties;
    this._combineFlagAndOptionalValue = sourceCommand._combineFlagAndOptionalValue;
    this._allowExcessArguments = sourceCommand._allowExcessArguments;
    this._enablePositionalOptions = sourceCommand._enablePositionalOptions;
    this._showHelpAfterError = sourceCommand._showHelpAfterError;
    this._showSuggestionAfterError = sourceCommand._showSuggestionAfterError;
    return this;
  }

  /**
   * @returns {Command[]}
   * @private
   */

  _getCommandAndAncestors() {
    const result = [];
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    for (let command = this; command; command = command.parent) {
      result.push(command);
    }
    return result;
  }

  /**
   * Define a command.
   *
   * There are two styles of command: pay attention to where to put the description.
   *
   * @example
   * // Command implemented using action handler (description is supplied separately to `.command`)
   * program
   *   .command('clone <source> [destination]')
   *   .description('clone a repository into a newly created directory')
   *   .action((source, destination) => {
   *     console.log('clone command called');
   *   });
   *
   * // Command implemented using separate executable file (description is second parameter to `.command`)
   * program
   *   .command('start <service>', 'start named service')
   *   .command('stop [service]', 'stop named service, or all if no name supplied');
   *
   * @param {string} nameAndArgs - command name and arguments, args are `<required>` or `[optional]` and last may also be `variadic...`
   * @param {(object | string)} [actionOptsOrExecDesc] - configuration options (for action), or description (for executable)
   * @param {object} [execOpts] - configuration options (for executable)
   * @return {Command} returns new command for action handler, or `this` for executable command
   */

  command(nameAndArgs, actionOptsOrExecDesc, execOpts) {
    let desc = actionOptsOrExecDesc;
    let opts = execOpts;
    if (typeof desc === 'object' && desc !== null) {
      opts = desc;
      desc = null;
    }
    opts = opts || {};
    const [, name, args] = nameAndArgs.match(/([^ ]+) *(.*)/);
    const cmd = this.createCommand(name);
    if (desc) {
      cmd.description(desc);
      cmd._executableHandler = true;
    }
    if (opts.isDefault) this._defaultCommandName = cmd._name;
    cmd._hidden = !!(opts.noHelp || opts.hidden); // noHelp is deprecated old name for hidden
    cmd._executableFile = opts.executableFile || null; // Custom name for executable file, set missing to null to match constructor
    if (args) cmd.arguments(args);
    this._registerCommand(cmd);
    cmd.parent = this;
    cmd.copyInheritedSettings(this);
    if (desc) return this;
    return cmd;
  }

  /**
   * Factory routine to create a new unattached command.
   *
   * See .command() for creating an attached subcommand, which uses this routine to
   * create the command. You can override createCommand to customise subcommands.
   *
   * @param {string} [name]
   * @return {Command} new command
   */

  createCommand(name) {
    return new Command(name);
  }

  /**
   * You can customise the help with a subclass of Help by overriding createHelp,
   * or by overriding Help properties using configureHelp().
   *
   * @return {Help}
   */

  createHelp() {
    return Object.assign(new Help$2(), this.configureHelp());
  }

  /**
   * You can customise the help by overriding Help properties using configureHelp(),
   * or with a subclass of Help by overriding createHelp().
   *
   * @param {object} [configuration] - configuration options
   * @return {(Command | object)} `this` command for chaining, or stored configuration
   */

  configureHelp(configuration) {
    if (configuration === undefined) return this._helpConfiguration;
    this._helpConfiguration = configuration;
    return this;
  }

  /**
   * The default output goes to stdout and stderr. You can customise this for special
   * applications. You can also customise the display of errors by overriding outputError.
   *
   * The configuration properties are all functions:
   *
   *     // functions to change where being written, stdout and stderr
   *     writeOut(str)
   *     writeErr(str)
   *     // matching functions to specify width for wrapping help
   *     getOutHelpWidth()
   *     getErrHelpWidth()
   *     // functions based on what is being written out
   *     outputError(str, write) // used for displaying errors, and not used for displaying help
   *
   * @param {object} [configuration] - configuration options
   * @return {(Command | object)} `this` command for chaining, or stored configuration
   */

  configureOutput(configuration) {
    if (configuration === undefined) return this._outputConfiguration;
    Object.assign(this._outputConfiguration, configuration);
    return this;
  }

  /**
   * Display the help or a custom message after an error occurs.
   *
   * @param {(boolean|string)} [displayHelp]
   * @return {Command} `this` command for chaining
   */
  showHelpAfterError(displayHelp = true) {
    if (typeof displayHelp !== 'string') displayHelp = !!displayHelp;
    this._showHelpAfterError = displayHelp;
    return this;
  }

  /**
   * Display suggestion of similar commands for unknown commands, or options for unknown options.
   *
   * @param {boolean} [displaySuggestion]
   * @return {Command} `this` command for chaining
   */
  showSuggestionAfterError(displaySuggestion = true) {
    this._showSuggestionAfterError = !!displaySuggestion;
    return this;
  }

  /**
   * Add a prepared subcommand.
   *
   * See .command() for creating an attached subcommand which inherits settings from its parent.
   *
   * @param {Command} cmd - new subcommand
   * @param {object} [opts] - configuration options
   * @return {Command} `this` command for chaining
   */

  addCommand(cmd, opts) {
    if (!cmd._name) {
      throw new Error(`Command passed to .addCommand() must have a name
- specify the name in Command constructor or using .name()`);
    }
    opts = opts || {};
    if (opts.isDefault) this._defaultCommandName = cmd._name;
    if (opts.noHelp || opts.hidden) cmd._hidden = true; // modifying passed command due to existing implementation

    this._registerCommand(cmd);
    cmd.parent = this;
    cmd._checkForBrokenPassThrough();
    return this;
  }

  /**
   * Factory routine to create a new unattached argument.
   *
   * See .argument() for creating an attached argument, which uses this routine to
   * create the argument. You can override createArgument to return a custom argument.
   *
   * @param {string} name
   * @param {string} [description]
   * @return {Argument} new argument
   */

  createArgument(name, description) {
    return new Argument$2(name, description);
  }

  /**
   * Define argument syntax for command.
   *
   * The default is that the argument is required, and you can explicitly
   * indicate this with <> around the name. Put [] around the name for an optional argument.
   *
   * @example
   * program.argument('<input-file>');
   * program.argument('[output-file]');
   *
   * @param {string} name
   * @param {string} [description]
   * @param {(Function|*)} [fn] - custom argument processing function
   * @param {*} [defaultValue]
   * @return {Command} `this` command for chaining
   */
  argument(name, description, fn, defaultValue) {
    const argument = this.createArgument(name, description);
    if (typeof fn === 'function') {
      argument.default(defaultValue).argParser(fn);
    } else {
      argument.default(fn);
    }
    this.addArgument(argument);
    return this;
  }

  /**
   * Define argument syntax for command, adding multiple at once (without descriptions).
   *
   * See also .argument().
   *
   * @example
   * program.arguments('<cmd> [env]');
   *
   * @param {string} names
   * @return {Command} `this` command for chaining
   */

  arguments(names) {
    names.trim().split(/ +/).forEach(detail => {
      this.argument(detail);
    });
    return this;
  }

  /**
   * Define argument syntax for command, adding a prepared argument.
   *
   * @param {Argument} argument
   * @return {Command} `this` command for chaining
   */
  addArgument(argument) {
    const previousArgument = this.registeredArguments.slice(-1)[0];
    if (previousArgument && previousArgument.variadic) {
      throw new Error(`only the last argument can be variadic '${previousArgument.name()}'`);
    }
    if (argument.required && argument.defaultValue !== undefined && argument.parseArg === undefined) {
      throw new Error(`a default value for a required argument is never used: '${argument.name()}'`);
    }
    this.registeredArguments.push(argument);
    return this;
  }

  /**
   * Customise or override default help command. By default a help command is automatically added if your command has subcommands.
   *
   * @example
   *    program.helpCommand('help [cmd]');
   *    program.helpCommand('help [cmd]', 'show help');
   *    program.helpCommand(false); // suppress default help command
   *    program.helpCommand(true); // add help command even if no subcommands
   *
   * @param {string|boolean} enableOrNameAndArgs - enable with custom name and/or arguments, or boolean to override whether added
   * @param {string} [description] - custom description
   * @return {Command} `this` command for chaining
   */

  helpCommand(enableOrNameAndArgs, description) {
    if (typeof enableOrNameAndArgs === 'boolean') {
      this._addImplicitHelpCommand = enableOrNameAndArgs;
      return this;
    }
    enableOrNameAndArgs = enableOrNameAndArgs ?? 'help [command]';
    const [, helpName, helpArgs] = enableOrNameAndArgs.match(/([^ ]+) *(.*)/);
    const helpDescription = description ?? 'display help for command';
    const helpCommand = this.createCommand(helpName);
    helpCommand.helpOption(false);
    if (helpArgs) helpCommand.arguments(helpArgs);
    if (helpDescription) helpCommand.description(helpDescription);
    this._addImplicitHelpCommand = true;
    this._helpCommand = helpCommand;
    return this;
  }

  /**
   * Add prepared custom help command.
   *
   * @param {(Command|string|boolean)} helpCommand - custom help command, or deprecated enableOrNameAndArgs as for `.helpCommand()`
   * @param {string} [deprecatedDescription] - deprecated custom description used with custom name only
   * @return {Command} `this` command for chaining
   */
  addHelpCommand(helpCommand, deprecatedDescription) {
    // If not passed an object, call through to helpCommand for backwards compatibility,
    // as addHelpCommand was originally used like helpCommand is now.
    if (typeof helpCommand !== 'object') {
      this.helpCommand(helpCommand, deprecatedDescription);
      return this;
    }
    this._addImplicitHelpCommand = true;
    this._helpCommand = helpCommand;
    return this;
  }

  /**
   * Lazy create help command.
   *
   * @return {(Command|null)}
   * @package
   */
  _getHelpCommand() {
    const hasImplicitHelpCommand = this._addImplicitHelpCommand ?? (this.commands.length && !this._actionHandler && !this._findCommand('help'));
    if (hasImplicitHelpCommand) {
      if (this._helpCommand === undefined) {
        this.helpCommand(undefined, undefined); // use default name and description
      }
      return this._helpCommand;
    }
    return null;
  }

  /**
   * Add hook for life cycle event.
   *
   * @param {string} event
   * @param {Function} listener
   * @return {Command} `this` command for chaining
   */

  hook(event, listener) {
    const allowedValues = ['preSubcommand', 'preAction', 'postAction'];
    if (!allowedValues.includes(event)) {
      throw new Error(`Unexpected value for event passed to hook : '${event}'.
Expecting one of '${allowedValues.join("', '")}'`);
    }
    if (this._lifeCycleHooks[event]) {
      this._lifeCycleHooks[event].push(listener);
    } else {
      this._lifeCycleHooks[event] = [listener];
    }
    return this;
  }

  /**
   * Register callback to use as replacement for calling process.exit.
   *
   * @param {Function} [fn] optional callback which will be passed a CommanderError, defaults to throwing
   * @return {Command} `this` command for chaining
   */

  exitOverride(fn) {
    if (fn) {
      this._exitCallback = fn;
    } else {
      this._exitCallback = err => {
        if (err.code !== 'commander.executeSubCommandAsync') {
          throw err;
        }
      };
    }
    return this;
  }

  /**
   * Call process.exit, and _exitCallback if defined.
   *
   * @param {number} exitCode exit code for using with process.exit
   * @param {string} code an id string representing the error
   * @param {string} message human-readable description of the error
   * @return never
   * @private
   */

  _exit(exitCode, code, message) {
    if (this._exitCallback) {
      this._exitCallback(new CommanderError$2(exitCode, code, message));
      // Expecting this line is not reached.
    }
    process$1.exit(exitCode);
  }

  /**
   * Register callback `fn` for the command.
   *
   * @example
   * program
   *   .command('serve')
   *   .description('start service')
   *   .action(function() {
   *      // do work here
   *   });
   *
   * @param {Function} fn
   * @return {Command} `this` command for chaining
   */

  action(fn) {
    const listener = args => {
      // The .action callback takes an extra parameter which is the command or options.
      const expectedArgsCount = this.registeredArguments.length;
      const actionArgs = args.slice(0, expectedArgsCount);
      if (this._storeOptionsAsProperties) {
        actionArgs[expectedArgsCount] = this; // backwards compatible "options"
      } else {
        actionArgs[expectedArgsCount] = this.opts();
      }
      actionArgs.push(this);
      return fn.apply(this, actionArgs);
    };
    this._actionHandler = listener;
    return this;
  }

  /**
   * Factory routine to create a new unattached option.
   *
   * See .option() for creating an attached option, which uses this routine to
   * create the option. You can override createOption to return a custom option.
   *
   * @param {string} flags
   * @param {string} [description]
   * @return {Option} new option
   */

  createOption(flags, description) {
    return new Option$2(flags, description);
  }

  /**
   * Wrap parseArgs to catch 'commander.invalidArgument'.
   *
   * @param {(Option | Argument)} target
   * @param {string} value
   * @param {*} previous
   * @param {string} invalidArgumentMessage
   * @private
   */

  _callParseArg(target, value, previous, invalidArgumentMessage) {
    try {
      return target.parseArg(value, previous);
    } catch (err) {
      if (err.code === 'commander.invalidArgument') {
        const message = `${invalidArgumentMessage} ${err.message}`;
        this.error(message, {
          exitCode: err.exitCode,
          code: err.code
        });
      }
      throw err;
    }
  }

  /**
   * Check for option flag conflicts.
   * Register option if no conflicts found, or throw on conflict.
   *
   * @param {Option} option
   * @private
   */

  _registerOption(option) {
    const matchingOption = option.short && this._findOption(option.short) || option.long && this._findOption(option.long);
    if (matchingOption) {
      const matchingFlag = option.long && this._findOption(option.long) ? option.long : option.short;
      throw new Error(`Cannot add option '${option.flags}'${this._name && ` to command '${this._name}'`} due to conflicting flag '${matchingFlag}'
-  already used by option '${matchingOption.flags}'`);
    }
    this.options.push(option);
  }

  /**
   * Check for command name and alias conflicts with existing commands.
   * Register command if no conflicts found, or throw on conflict.
   *
   * @param {Command} command
   * @private
   */

  _registerCommand(command) {
    const knownBy = cmd => {
      return [cmd.name()].concat(cmd.aliases());
    };
    const alreadyUsed = knownBy(command).find(name => this._findCommand(name));
    if (alreadyUsed) {
      const existingCmd = knownBy(this._findCommand(alreadyUsed)).join('|');
      const newCmd = knownBy(command).join('|');
      throw new Error(`cannot add command '${newCmd}' as already have command '${existingCmd}'`);
    }
    this.commands.push(command);
  }

  /**
   * Add an option.
   *
   * @param {Option} option
   * @return {Command} `this` command for chaining
   */
  addOption(option) {
    this._registerOption(option);
    const oname = option.name();
    const name = option.attributeName();

    // store default value
    if (option.negate) {
      // --no-foo is special and defaults foo to true, unless a --foo option is already defined
      const positiveLongFlag = option.long.replace(/^--no-/, '--');
      if (!this._findOption(positiveLongFlag)) {
        this.setOptionValueWithSource(name, option.defaultValue === undefined ? true : option.defaultValue, 'default');
      }
    } else if (option.defaultValue !== undefined) {
      this.setOptionValueWithSource(name, option.defaultValue, 'default');
    }

    // handler for cli and env supplied values
    const handleOptionValue = (val, invalidValueMessage, valueSource) => {
      // val is null for optional option used without an optional-argument.
      // val is undefined for boolean and negated option.
      if (val == null && option.presetArg !== undefined) {
        val = option.presetArg;
      }

      // custom processing
      const oldValue = this.getOptionValue(name);
      if (val !== null && option.parseArg) {
        val = this._callParseArg(option, val, oldValue, invalidValueMessage);
      } else if (val !== null && option.variadic) {
        val = option._concatValue(val, oldValue);
      }

      // Fill-in appropriate missing values. Long winded but easy to follow.
      if (val == null) {
        if (option.negate) {
          val = false;
        } else if (option.isBoolean() || option.optional) {
          val = true;
        } else {
          val = ''; // not normal, parseArg might have failed or be a mock function for testing
        }
      }
      this.setOptionValueWithSource(name, val, valueSource);
    };
    this.on('option:' + oname, val => {
      const invalidValueMessage = `error: option '${option.flags}' argument '${val}' is invalid.`;
      handleOptionValue(val, invalidValueMessage, 'cli');
    });
    if (option.envVar) {
      this.on('optionEnv:' + oname, val => {
        const invalidValueMessage = `error: option '${option.flags}' value '${val}' from env '${option.envVar}' is invalid.`;
        handleOptionValue(val, invalidValueMessage, 'env');
      });
    }
    return this;
  }

  /**
   * Internal implementation shared by .option() and .requiredOption()
   *
   * @return {Command} `this` command for chaining
   * @private
   */
  _optionEx(config, flags, description, fn, defaultValue) {
    if (typeof flags === 'object' && flags instanceof Option$2) {
      throw new Error('To add an Option object use addOption() instead of option() or requiredOption()');
    }
    const option = this.createOption(flags, description);
    option.makeOptionMandatory(!!config.mandatory);
    if (typeof fn === 'function') {
      option.default(defaultValue).argParser(fn);
    } else if (fn instanceof RegExp) {
      // deprecated
      const regex = fn;
      fn = (val, def) => {
        const m = regex.exec(val);
        return m ? m[0] : def;
      };
      option.default(defaultValue).argParser(fn);
    } else {
      option.default(fn);
    }
    return this.addOption(option);
  }

  /**
   * Define option with `flags`, `description`, and optional argument parsing function or `defaultValue` or both.
   *
   * The `flags` string contains the short and/or long flags, separated by comma, a pipe or space. A required
   * option-argument is indicated by `<>` and an optional option-argument by `[]`.
   *
   * See the README for more details, and see also addOption() and requiredOption().
   *
   * @example
   * program
   *     .option('-p, --pepper', 'add pepper')
   *     .option('-p, --pizza-type <TYPE>', 'type of pizza') // required option-argument
   *     .option('-c, --cheese [CHEESE]', 'add extra cheese', 'mozzarella') // optional option-argument with default
   *     .option('-t, --tip <VALUE>', 'add tip to purchase cost', parseFloat) // custom parse function
   *
   * @param {string} flags
   * @param {string} [description]
   * @param {(Function|*)} [parseArg] - custom option processing function or default value
   * @param {*} [defaultValue]
   * @return {Command} `this` command for chaining
   */

  option(flags, description, parseArg, defaultValue) {
    return this._optionEx({}, flags, description, parseArg, defaultValue);
  }

  /**
   * Add a required option which must have a value after parsing. This usually means
   * the option must be specified on the command line. (Otherwise the same as .option().)
   *
   * The `flags` string contains the short and/or long flags, separated by comma, a pipe or space.
   *
   * @param {string} flags
   * @param {string} [description]
   * @param {(Function|*)} [parseArg] - custom option processing function or default value
   * @param {*} [defaultValue]
   * @return {Command} `this` command for chaining
   */

  requiredOption(flags, description, parseArg, defaultValue) {
    return this._optionEx({
      mandatory: true
    }, flags, description, parseArg, defaultValue);
  }

  /**
   * Alter parsing of short flags with optional values.
   *
   * @example
   * // for `.option('-f,--flag [value]'):
   * program.combineFlagAndOptionalValue(true);  // `-f80` is treated like `--flag=80`, this is the default behaviour
   * program.combineFlagAndOptionalValue(false) // `-fb` is treated like `-f -b`
   *
   * @param {boolean} [combine] - if `true` or omitted, an optional value can be specified directly after the flag.
   * @return {Command} `this` command for chaining
   */
  combineFlagAndOptionalValue(combine = true) {
    this._combineFlagAndOptionalValue = !!combine;
    return this;
  }

  /**
   * Allow unknown options on the command line.
   *
   * @param {boolean} [allowUnknown] - if `true` or omitted, no error will be thrown for unknown options.
   * @return {Command} `this` command for chaining
   */
  allowUnknownOption(allowUnknown = true) {
    this._allowUnknownOption = !!allowUnknown;
    return this;
  }

  /**
   * Allow excess command-arguments on the command line. Pass false to make excess arguments an error.
   *
   * @param {boolean} [allowExcess] - if `true` or omitted, no error will be thrown for excess arguments.
   * @return {Command} `this` command for chaining
   */
  allowExcessArguments(allowExcess = true) {
    this._allowExcessArguments = !!allowExcess;
    return this;
  }

  /**
   * Enable positional options. Positional means global options are specified before subcommands which lets
   * subcommands reuse the same option names, and also enables subcommands to turn on passThroughOptions.
   * The default behaviour is non-positional and global options may appear anywhere on the command line.
   *
   * @param {boolean} [positional]
   * @return {Command} `this` command for chaining
   */
  enablePositionalOptions(positional = true) {
    this._enablePositionalOptions = !!positional;
    return this;
  }

  /**
   * Pass through options that come after command-arguments rather than treat them as command-options,
   * so actual command-options come before command-arguments. Turning this on for a subcommand requires
   * positional options to have been enabled on the program (parent commands).
   * The default behaviour is non-positional and options may appear before or after command-arguments.
   *
   * @param {boolean} [passThrough] for unknown options.
   * @return {Command} `this` command for chaining
   */
  passThroughOptions(passThrough = true) {
    this._passThroughOptions = !!passThrough;
    this._checkForBrokenPassThrough();
    return this;
  }

  /**
   * @private
   */

  _checkForBrokenPassThrough() {
    if (this.parent && this._passThroughOptions && !this.parent._enablePositionalOptions) {
      throw new Error(`passThroughOptions cannot be used for '${this._name}' without turning on enablePositionalOptions for parent command(s)`);
    }
  }

  /**
   * Whether to store option values as properties on command object,
   * or store separately (specify false). In both cases the option values can be accessed using .opts().
   *
   * @param {boolean} [storeAsProperties=true]
   * @return {Command} `this` command for chaining
   */

  storeOptionsAsProperties(storeAsProperties = true) {
    if (this.options.length) {
      throw new Error('call .storeOptionsAsProperties() before adding options');
    }
    if (Object.keys(this._optionValues).length) {
      throw new Error('call .storeOptionsAsProperties() before setting option values');
    }
    this._storeOptionsAsProperties = !!storeAsProperties;
    return this;
  }

  /**
   * Retrieve option value.
   *
   * @param {string} key
   * @return {object} value
   */

  getOptionValue(key) {
    if (this._storeOptionsAsProperties) {
      return this[key];
    }
    return this._optionValues[key];
  }

  /**
   * Store option value.
   *
   * @param {string} key
   * @param {object} value
   * @return {Command} `this` command for chaining
   */

  setOptionValue(key, value) {
    return this.setOptionValueWithSource(key, value, undefined);
  }

  /**
   * Store option value and where the value came from.
   *
   * @param {string} key
   * @param {object} value
   * @param {string} source - expected values are default/config/env/cli/implied
   * @return {Command} `this` command for chaining
   */

  setOptionValueWithSource(key, value, source) {
    if (this._storeOptionsAsProperties) {
      this[key] = value;
    } else {
      this._optionValues[key] = value;
    }
    this._optionValueSources[key] = source;
    return this;
  }

  /**
   * Get source of option value.
   * Expected values are default | config | env | cli | implied
   *
   * @param {string} key
   * @return {string}
   */

  getOptionValueSource(key) {
    return this._optionValueSources[key];
  }

  /**
   * Get source of option value. See also .optsWithGlobals().
   * Expected values are default | config | env | cli | implied
   *
   * @param {string} key
   * @return {string}
   */

  getOptionValueSourceWithGlobals(key) {
    // global overwrites local, like optsWithGlobals
    let source;
    this._getCommandAndAncestors().forEach(cmd => {
      if (cmd.getOptionValueSource(key) !== undefined) {
        source = cmd.getOptionValueSource(key);
      }
    });
    return source;
  }

  /**
   * Get user arguments from implied or explicit arguments.
   * Side-effects: set _scriptPath if args included script. Used for default program name, and subcommand searches.
   *
   * @private
   */

  _prepareUserArgs(argv, parseOptions) {
    if (argv !== undefined && !Array.isArray(argv)) {
      throw new Error('first parameter to parse must be array or undefined');
    }
    parseOptions = parseOptions || {};

    // auto-detect argument conventions if nothing supplied
    if (argv === undefined && parseOptions.from === undefined) {
      if (process$1.versions?.electron) {
        parseOptions.from = 'electron';
      }
      // check node specific options for scenarios where user CLI args follow executable without scriptname
      const execArgv = process$1.execArgv ?? [];
      if (execArgv.includes('-e') || execArgv.includes('--eval') || execArgv.includes('-p') || execArgv.includes('--print')) {
        parseOptions.from = 'eval'; // internal usage, not documented
      }
    }

    // default to using process.argv
    if (argv === undefined) {
      argv = process$1.argv;
    }
    this.rawArgs = argv.slice();

    // extract the user args and scriptPath
    let userArgs;
    switch (parseOptions.from) {
      case undefined:
      case 'node':
        this._scriptPath = argv[1];
        userArgs = argv.slice(2);
        break;
      case 'electron':
        // @ts-ignore: because defaultApp is an unknown property
        if (process$1.defaultApp) {
          this._scriptPath = argv[1];
          userArgs = argv.slice(2);
        } else {
          userArgs = argv.slice(1);
        }
        break;
      case 'user':
        userArgs = argv.slice(0);
        break;
      case 'eval':
        userArgs = argv.slice(1);
        break;
      default:
        throw new Error(`unexpected parse option { from: '${parseOptions.from}' }`);
    }

    // Find default name for program from arguments.
    if (!this._name && this._scriptPath) this.nameFromFilename(this._scriptPath);
    this._name = this._name || 'program';
    return userArgs;
  }

  /**
   * Parse `argv`, setting options and invoking commands when defined.
   *
   * Use parseAsync instead of parse if any of your action handlers are async.
   *
   * Call with no parameters to parse `process.argv`. Detects Electron and special node options like `node --eval`. Easy mode!
   *
   * Or call with an array of strings to parse, and optionally where the user arguments start by specifying where the arguments are `from`:
   * - `'node'`: default, `argv[0]` is the application and `argv[1]` is the script being run, with user arguments after that
   * - `'electron'`: `argv[0]` is the application and `argv[1]` varies depending on whether the electron application is packaged
   * - `'user'`: just user arguments
   *
   * @example
   * program.parse(); // parse process.argv and auto-detect electron and special node flags
   * program.parse(process.argv); // assume argv[0] is app and argv[1] is script
   * program.parse(my-args, { from: 'user' }); // just user supplied arguments, nothing special about argv[0]
   *
   * @param {string[]} [argv] - optional, defaults to process.argv
   * @param {object} [parseOptions] - optionally specify style of options with from: node/user/electron
   * @param {string} [parseOptions.from] - where the args are from: 'node', 'user', 'electron'
   * @return {Command} `this` command for chaining
   */

  parse(argv, parseOptions) {
    const userArgs = this._prepareUserArgs(argv, parseOptions);
    this._parseCommand([], userArgs);
    return this;
  }

  /**
   * Parse `argv`, setting options and invoking commands when defined.
   *
   * Call with no parameters to parse `process.argv`. Detects Electron and special node options like `node --eval`. Easy mode!
   *
   * Or call with an array of strings to parse, and optionally where the user arguments start by specifying where the arguments are `from`:
   * - `'node'`: default, `argv[0]` is the application and `argv[1]` is the script being run, with user arguments after that
   * - `'electron'`: `argv[0]` is the application and `argv[1]` varies depending on whether the electron application is packaged
   * - `'user'`: just user arguments
   *
   * @example
   * await program.parseAsync(); // parse process.argv and auto-detect electron and special node flags
   * await program.parseAsync(process.argv); // assume argv[0] is app and argv[1] is script
   * await program.parseAsync(my-args, { from: 'user' }); // just user supplied arguments, nothing special about argv[0]
   *
   * @param {string[]} [argv]
   * @param {object} [parseOptions]
   * @param {string} parseOptions.from - where the args are from: 'node', 'user', 'electron'
   * @return {Promise}
   */

  async parseAsync(argv, parseOptions) {
    const userArgs = this._prepareUserArgs(argv, parseOptions);
    await this._parseCommand([], userArgs);
    return this;
  }

  /**
   * Execute a sub-command executable.
   *
   * @private
   */

  _executeSubCommand(subcommand, args) {
    args = args.slice();
    let launchWithNode = false; // Use node for source targets so do not need to get permissions correct, and on Windows.
    const sourceExt = ['.js', '.ts', '.tsx', '.mjs', '.cjs'];
    function findFile(baseDir, baseName) {
      // Look for specified file
      const localBin = path.resolve(baseDir, baseName);
      if (fs.existsSync(localBin)) return localBin;

      // Stop looking if candidate already has an expected extension.
      if (sourceExt.includes(path.extname(baseName))) return undefined;

      // Try all the extensions.
      const foundExt = sourceExt.find(ext => fs.existsSync(`${localBin}${ext}`));
      if (foundExt) return `${localBin}${foundExt}`;
      return undefined;
    }

    // Not checking for help first. Unlikely to have mandatory and executable, and can't robustly test for help flags in external command.
    this._checkForMissingMandatoryOptions();
    this._checkForConflictingOptions();

    // executableFile and executableDir might be full path, or just a name
    let executableFile = subcommand._executableFile || `${this._name}-${subcommand._name}`;
    let executableDir = this._executableDir || '';
    if (this._scriptPath) {
      let resolvedScriptPath; // resolve possible symlink for installed npm binary
      try {
        resolvedScriptPath = fs.realpathSync(this._scriptPath);
      } catch (err) {
        resolvedScriptPath = this._scriptPath;
      }
      executableDir = path.resolve(path.dirname(resolvedScriptPath), executableDir);
    }

    // Look for a local file in preference to a command in PATH.
    if (executableDir) {
      let localFile = findFile(executableDir, executableFile);

      // Legacy search using prefix of script name instead of command name
      if (!localFile && !subcommand._executableFile && this._scriptPath) {
        const legacyName = path.basename(this._scriptPath, path.extname(this._scriptPath));
        if (legacyName !== this._name) {
          localFile = findFile(executableDir, `${legacyName}-${subcommand._name}`);
        }
      }
      executableFile = localFile || executableFile;
    }
    launchWithNode = sourceExt.includes(path.extname(executableFile));
    let proc;
    if (process$1.platform !== 'win32') {
      if (launchWithNode) {
        args.unshift(executableFile);
        // add executable arguments to spawn
        args = incrementNodeInspectorPort(process$1.execArgv).concat(args);
        proc = childProcess.spawn(process$1.argv[0], args, {
          stdio: 'inherit'
        });
      } else {
        proc = childProcess.spawn(executableFile, args, {
          stdio: 'inherit'
        });
      }
    } else {
      args.unshift(executableFile);
      // add executable arguments to spawn
      args = incrementNodeInspectorPort(process$1.execArgv).concat(args);
      proc = childProcess.spawn(process$1.execPath, args, {
        stdio: 'inherit'
      });
    }
    if (!proc.killed) {
      // testing mainly to avoid leak warnings during unit tests with mocked spawn
      const signals = ['SIGUSR1', 'SIGUSR2', 'SIGTERM', 'SIGINT', 'SIGHUP'];
      signals.forEach(signal => {
        process$1.on(signal, () => {
          if (proc.killed === false && proc.exitCode === null) {
            // @ts-ignore because signals not typed to known strings
            proc.kill(signal);
          }
        });
      });
    }

    // By default terminate process when spawned process terminates.
    const exitCallback = this._exitCallback;
    proc.on('close', code => {
      code = code ?? 1; // code is null if spawned process terminated due to a signal
      if (!exitCallback) {
        process$1.exit(code);
      } else {
        exitCallback(new CommanderError$2(code, 'commander.executeSubCommandAsync', '(close)'));
      }
    });
    proc.on('error', err => {
      // @ts-ignore: because err.code is an unknown property
      if (err.code === 'ENOENT') {
        const executableDirMessage = executableDir ? `searched for local subcommand relative to directory '${executableDir}'` : 'no directory for search for local subcommand, use .executableDir() to supply a custom directory';
        const executableMissing = `'${executableFile}' does not exist
 - if '${subcommand._name}' is not meant to be an executable command, remove description parameter from '.command()' and use '.description()' instead
 - if the default executable name is not suitable, use the executableFile option to supply a custom name or path
 - ${executableDirMessage}`;
        throw new Error(executableMissing);
        // @ts-ignore: because err.code is an unknown property
      } else if (err.code === 'EACCES') {
        throw new Error(`'${executableFile}' not executable`);
      }
      if (!exitCallback) {
        process$1.exit(1);
      } else {
        const wrappedError = new CommanderError$2(1, 'commander.executeSubCommandAsync', '(error)');
        wrappedError.nestedError = err;
        exitCallback(wrappedError);
      }
    });

    // Store the reference to the child process
    this.runningCommand = proc;
  }

  /**
   * @private
   */

  _dispatchSubcommand(commandName, operands, unknown) {
    const subCommand = this._findCommand(commandName);
    if (!subCommand) this.help({
      error: true
    });
    let promiseChain;
    promiseChain = this._chainOrCallSubCommandHook(promiseChain, subCommand, 'preSubcommand');
    promiseChain = this._chainOrCall(promiseChain, () => {
      if (subCommand._executableHandler) {
        this._executeSubCommand(subCommand, operands.concat(unknown));
      } else {
        return subCommand._parseCommand(operands, unknown);
      }
    });
    return promiseChain;
  }

  /**
   * Invoke help directly if possible, or dispatch if necessary.
   * e.g. help foo
   *
   * @private
   */

  _dispatchHelpCommand(subcommandName) {
    if (!subcommandName) {
      this.help();
    }
    const subCommand = this._findCommand(subcommandName);
    if (subCommand && !subCommand._executableHandler) {
      subCommand.help();
    }

    // Fallback to parsing the help flag to invoke the help.
    return this._dispatchSubcommand(subcommandName, [], [this._getHelpOption()?.long ?? this._getHelpOption()?.short ?? '--help']);
  }

  /**
   * Check this.args against expected this.registeredArguments.
   *
   * @private
   */

  _checkNumberOfArguments() {
    // too few
    this.registeredArguments.forEach((arg, i) => {
      if (arg.required && this.args[i] == null) {
        this.missingArgument(arg.name());
      }
    });
    // too many
    if (this.registeredArguments.length > 0 && this.registeredArguments[this.registeredArguments.length - 1].variadic) {
      return;
    }
    if (this.args.length > this.registeredArguments.length) {
      this._excessArguments(this.args);
    }
  }

  /**
   * Process this.args using this.registeredArguments and save as this.processedArgs!
   *
   * @private
   */

  _processArguments() {
    const myParseArg = (argument, value, previous) => {
      // Extra processing for nice error message on parsing failure.
      let parsedValue = value;
      if (value !== null && argument.parseArg) {
        const invalidValueMessage = `error: command-argument value '${value}' is invalid for argument '${argument.name()}'.`;
        parsedValue = this._callParseArg(argument, value, previous, invalidValueMessage);
      }
      return parsedValue;
    };
    this._checkNumberOfArguments();
    const processedArgs = [];
    this.registeredArguments.forEach((declaredArg, index) => {
      let value = declaredArg.defaultValue;
      if (declaredArg.variadic) {
        // Collect together remaining arguments for passing together as an array.
        if (index < this.args.length) {
          value = this.args.slice(index);
          if (declaredArg.parseArg) {
            value = value.reduce((processed, v) => {
              return myParseArg(declaredArg, v, processed);
            }, declaredArg.defaultValue);
          }
        } else if (value === undefined) {
          value = [];
        }
      } else if (index < this.args.length) {
        value = this.args[index];
        if (declaredArg.parseArg) {
          value = myParseArg(declaredArg, value, declaredArg.defaultValue);
        }
      }
      processedArgs[index] = value;
    });
    this.processedArgs = processedArgs;
  }

  /**
   * Once we have a promise we chain, but call synchronously until then.
   *
   * @param {(Promise|undefined)} promise
   * @param {Function} fn
   * @return {(Promise|undefined)}
   * @private
   */

  _chainOrCall(promise, fn) {
    // thenable
    if (promise && promise.then && typeof promise.then === 'function') {
      // already have a promise, chain callback
      return promise.then(() => fn());
    }
    // callback might return a promise
    return fn();
  }

  /**
   *
   * @param {(Promise|undefined)} promise
   * @param {string} event
   * @return {(Promise|undefined)}
   * @private
   */

  _chainOrCallHooks(promise, event) {
    let result = promise;
    const hooks = [];
    this._getCommandAndAncestors().reverse().filter(cmd => cmd._lifeCycleHooks[event] !== undefined).forEach(hookedCommand => {
      hookedCommand._lifeCycleHooks[event].forEach(callback => {
        hooks.push({
          hookedCommand,
          callback
        });
      });
    });
    if (event === 'postAction') {
      hooks.reverse();
    }
    hooks.forEach(hookDetail => {
      result = this._chainOrCall(result, () => {
        return hookDetail.callback(hookDetail.hookedCommand, this);
      });
    });
    return result;
  }

  /**
   *
   * @param {(Promise|undefined)} promise
   * @param {Command} subCommand
   * @param {string} event
   * @return {(Promise|undefined)}
   * @private
   */

  _chainOrCallSubCommandHook(promise, subCommand, event) {
    let result = promise;
    if (this._lifeCycleHooks[event] !== undefined) {
      this._lifeCycleHooks[event].forEach(hook => {
        result = this._chainOrCall(result, () => {
          return hook(this, subCommand);
        });
      });
    }
    return result;
  }

  /**
   * Process arguments in context of this command.
   * Returns action result, in case it is a promise.
   *
   * @private
   */

  _parseCommand(operands, unknown) {
    const parsed = this.parseOptions(unknown);
    this._parseOptionsEnv(); // after cli, so parseArg not called on both cli and env
    this._parseOptionsImplied();
    operands = operands.concat(parsed.operands);
    unknown = parsed.unknown;
    this.args = operands.concat(unknown);
    if (operands && this._findCommand(operands[0])) {
      return this._dispatchSubcommand(operands[0], operands.slice(1), unknown);
    }
    if (this._getHelpCommand() && operands[0] === this._getHelpCommand().name()) {
      return this._dispatchHelpCommand(operands[1]);
    }
    if (this._defaultCommandName) {
      this._outputHelpIfRequested(unknown); // Run the help for default command from parent rather than passing to default command
      return this._dispatchSubcommand(this._defaultCommandName, operands, unknown);
    }
    if (this.commands.length && this.args.length === 0 && !this._actionHandler && !this._defaultCommandName) {
      // probably missing subcommand and no handler, user needs help (and exit)
      this.help({
        error: true
      });
    }
    this._outputHelpIfRequested(parsed.unknown);
    this._checkForMissingMandatoryOptions();
    this._checkForConflictingOptions();

    // We do not always call this check to avoid masking a "better" error, like unknown command.
    const checkForUnknownOptions = () => {
      if (parsed.unknown.length > 0) {
        this.unknownOption(parsed.unknown[0]);
      }
    };
    const commandEvent = `command:${this.name()}`;
    if (this._actionHandler) {
      checkForUnknownOptions();
      this._processArguments();
      let promiseChain;
      promiseChain = this._chainOrCallHooks(promiseChain, 'preAction');
      promiseChain = this._chainOrCall(promiseChain, () => this._actionHandler(this.processedArgs));
      if (this.parent) {
        promiseChain = this._chainOrCall(promiseChain, () => {
          this.parent.emit(commandEvent, operands, unknown); // legacy
        });
      }
      promiseChain = this._chainOrCallHooks(promiseChain, 'postAction');
      return promiseChain;
    }
    if (this.parent && this.parent.listenerCount(commandEvent)) {
      checkForUnknownOptions();
      this._processArguments();
      this.parent.emit(commandEvent, operands, unknown); // legacy
    } else if (operands.length) {
      if (this._findCommand('*')) {
        // legacy default command
        return this._dispatchSubcommand('*', operands, unknown);
      }
      if (this.listenerCount('command:*')) {
        // skip option check, emit event for possible misspelling suggestion
        this.emit('command:*', operands, unknown);
      } else if (this.commands.length) {
        this.unknownCommand();
      } else {
        checkForUnknownOptions();
        this._processArguments();
      }
    } else if (this.commands.length) {
      checkForUnknownOptions();
      // This command has subcommands and nothing hooked up at this level, so display help (and exit).
      this.help({
        error: true
      });
    } else {
      checkForUnknownOptions();
      this._processArguments();
      // fall through for caller to handle after calling .parse()
    }
  }

  /**
   * Find matching command.
   *
   * @private
   * @return {Command | undefined}
   */
  _findCommand(name) {
    if (!name) return undefined;
    return this.commands.find(cmd => cmd._name === name || cmd._aliases.includes(name));
  }

  /**
   * Return an option matching `arg` if any.
   *
   * @param {string} arg
   * @return {Option}
   * @package
   */

  _findOption(arg) {
    return this.options.find(option => option.is(arg));
  }

  /**
   * Display an error message if a mandatory option does not have a value.
   * Called after checking for help flags in leaf subcommand.
   *
   * @private
   */

  _checkForMissingMandatoryOptions() {
    // Walk up hierarchy so can call in subcommand after checking for displaying help.
    this._getCommandAndAncestors().forEach(cmd => {
      cmd.options.forEach(anOption => {
        if (anOption.mandatory && cmd.getOptionValue(anOption.attributeName()) === undefined) {
          cmd.missingMandatoryOptionValue(anOption);
        }
      });
    });
  }

  /**
   * Display an error message if conflicting options are used together in this.
   *
   * @private
   */
  _checkForConflictingLocalOptions() {
    const definedNonDefaultOptions = this.options.filter(option => {
      const optionKey = option.attributeName();
      if (this.getOptionValue(optionKey) === undefined) {
        return false;
      }
      return this.getOptionValueSource(optionKey) !== 'default';
    });
    const optionsWithConflicting = definedNonDefaultOptions.filter(option => option.conflictsWith.length > 0);
    optionsWithConflicting.forEach(option => {
      const conflictingAndDefined = definedNonDefaultOptions.find(defined => option.conflictsWith.includes(defined.attributeName()));
      if (conflictingAndDefined) {
        this._conflictingOption(option, conflictingAndDefined);
      }
    });
  }

  /**
   * Display an error message if conflicting options are used together.
   * Called after checking for help flags in leaf subcommand.
   *
   * @private
   */
  _checkForConflictingOptions() {
    // Walk up hierarchy so can call in subcommand after checking for displaying help.
    this._getCommandAndAncestors().forEach(cmd => {
      cmd._checkForConflictingLocalOptions();
    });
  }

  /**
   * Parse options from `argv` removing known options,
   * and return argv split into operands and unknown arguments.
   *
   * Examples:
   *
   *     argv => operands, unknown
   *     --known kkk op => [op], []
   *     op --known kkk => [op], []
   *     sub --unknown uuu op => [sub], [--unknown uuu op]
   *     sub -- --unknown uuu op => [sub --unknown uuu op], []
   *
   * @param {string[]} argv
   * @return {{operands: string[], unknown: string[]}}
   */

  parseOptions(argv) {
    const operands = []; // operands, not options or values
    const unknown = []; // first unknown option and remaining unknown args
    let dest = operands;
    const args = argv.slice();
    function maybeOption(arg) {
      return arg.length > 1 && arg[0] === '-';
    }

    // parse options
    let activeVariadicOption = null;
    while (args.length) {
      const arg = args.shift();

      // literal
      if (arg === '--') {
        if (dest === unknown) dest.push(arg);
        dest.push(...args);
        break;
      }
      if (activeVariadicOption && !maybeOption(arg)) {
        this.emit(`option:${activeVariadicOption.name()}`, arg);
        continue;
      }
      activeVariadicOption = null;
      if (maybeOption(arg)) {
        const option = this._findOption(arg);
        // recognised option, call listener to assign value with possible custom processing
        if (option) {
          if (option.required) {
            const value = args.shift();
            if (value === undefined) this.optionMissingArgument(option);
            this.emit(`option:${option.name()}`, value);
          } else if (option.optional) {
            let value = null;
            // historical behaviour is optional value is following arg unless an option
            if (args.length > 0 && !maybeOption(args[0])) {
              value = args.shift();
            }
            this.emit(`option:${option.name()}`, value);
          } else {
            // boolean flag
            this.emit(`option:${option.name()}`);
          }
          activeVariadicOption = option.variadic ? option : null;
          continue;
        }
      }

      // Look for combo options following single dash, eat first one if known.
      if (arg.length > 2 && arg[0] === '-' && arg[1] !== '-') {
        const option = this._findOption(`-${arg[1]}`);
        if (option) {
          if (option.required || option.optional && this._combineFlagAndOptionalValue) {
            // option with value following in same argument
            this.emit(`option:${option.name()}`, arg.slice(2));
          } else {
            // boolean option, emit and put back remainder of arg for further processing
            this.emit(`option:${option.name()}`);
            args.unshift(`-${arg.slice(2)}`);
          }
          continue;
        }
      }

      // Look for known long flag with value, like --foo=bar
      if (/^--[^=]+=/.test(arg)) {
        const index = arg.indexOf('=');
        const option = this._findOption(arg.slice(0, index));
        if (option && (option.required || option.optional)) {
          this.emit(`option:${option.name()}`, arg.slice(index + 1));
          continue;
        }
      }

      // Not a recognised option by this command.
      // Might be a command-argument, or subcommand option, or unknown option, or help command or option.

      // An unknown option means further arguments also classified as unknown so can be reprocessed by subcommands.
      if (maybeOption(arg)) {
        dest = unknown;
      }

      // If using positionalOptions, stop processing our options at subcommand.
      if ((this._enablePositionalOptions || this._passThroughOptions) && operands.length === 0 && unknown.length === 0) {
        if (this._findCommand(arg)) {
          operands.push(arg);
          if (args.length > 0) unknown.push(...args);
          break;
        } else if (this._getHelpCommand() && arg === this._getHelpCommand().name()) {
          operands.push(arg);
          if (args.length > 0) operands.push(...args);
          break;
        } else if (this._defaultCommandName) {
          unknown.push(arg);
          if (args.length > 0) unknown.push(...args);
          break;
        }
      }

      // If using passThroughOptions, stop processing options at first command-argument.
      if (this._passThroughOptions) {
        dest.push(arg);
        if (args.length > 0) dest.push(...args);
        break;
      }

      // add arg
      dest.push(arg);
    }
    return {
      operands,
      unknown
    };
  }

  /**
   * Return an object containing local option values as key-value pairs.
   *
   * @return {object}
   */
  opts() {
    if (this._storeOptionsAsProperties) {
      // Preserve original behaviour so backwards compatible when still using properties
      const result = {};
      const len = this.options.length;
      for (let i = 0; i < len; i++) {
        const key = this.options[i].attributeName();
        result[key] = key === this._versionOptionName ? this._version : this[key];
      }
      return result;
    }
    return this._optionValues;
  }

  /**
   * Return an object containing merged local and global option values as key-value pairs.
   *
   * @return {object}
   */
  optsWithGlobals() {
    // globals overwrite locals
    return this._getCommandAndAncestors().reduce((combinedOptions, cmd) => Object.assign(combinedOptions, cmd.opts()), {});
  }

  /**
   * Display error message and exit (or call exitOverride).
   *
   * @param {string} message
   * @param {object} [errorOptions]
   * @param {string} [errorOptions.code] - an id string representing the error
   * @param {number} [errorOptions.exitCode] - used with process.exit
   */
  error(message, errorOptions) {
    // output handling
    this._outputConfiguration.outputError(`${message}\n`, this._outputConfiguration.writeErr);
    if (typeof this._showHelpAfterError === 'string') {
      this._outputConfiguration.writeErr(`${this._showHelpAfterError}\n`);
    } else if (this._showHelpAfterError) {
      this._outputConfiguration.writeErr('\n');
      this.outputHelp({
        error: true
      });
    }

    // exit handling
    const config = errorOptions || {};
    const exitCode = config.exitCode || 1;
    const code = config.code || 'commander.error';
    this._exit(exitCode, code, message);
  }

  /**
   * Apply any option related environment variables, if option does
   * not have a value from cli or client code.
   *
   * @private
   */
  _parseOptionsEnv() {
    this.options.forEach(option => {
      if (option.envVar && option.envVar in process$1.env) {
        const optionKey = option.attributeName();
        // Priority check. Do not overwrite cli or options from unknown source (client-code).
        if (this.getOptionValue(optionKey) === undefined || ['default', 'config', 'env'].includes(this.getOptionValueSource(optionKey))) {
          if (option.required || option.optional) {
            // option can take a value
            // keep very simple, optional always takes value
            this.emit(`optionEnv:${option.name()}`, process$1.env[option.envVar]);
          } else {
            // boolean
            // keep very simple, only care that envVar defined and not the value
            this.emit(`optionEnv:${option.name()}`);
          }
        }
      }
    });
  }

  /**
   * Apply any implied option values, if option is undefined or default value.
   *
   * @private
   */
  _parseOptionsImplied() {
    const dualHelper = new DualOptions(this.options);
    const hasCustomOptionValue = optionKey => {
      return this.getOptionValue(optionKey) !== undefined && !['default', 'implied'].includes(this.getOptionValueSource(optionKey));
    };
    this.options.filter(option => option.implied !== undefined && hasCustomOptionValue(option.attributeName()) && dualHelper.valueFromOption(this.getOptionValue(option.attributeName()), option)).forEach(option => {
      Object.keys(option.implied).filter(impliedKey => !hasCustomOptionValue(impliedKey)).forEach(impliedKey => {
        this.setOptionValueWithSource(impliedKey, option.implied[impliedKey], 'implied');
      });
    });
  }

  /**
   * Argument `name` is missing.
   *
   * @param {string} name
   * @private
   */

  missingArgument(name) {
    const message = `error: missing required argument '${name}'`;
    this.error(message, {
      code: 'commander.missingArgument'
    });
  }

  /**
   * `Option` is missing an argument.
   *
   * @param {Option} option
   * @private
   */

  optionMissingArgument(option) {
    const message = `error: option '${option.flags}' argument missing`;
    this.error(message, {
      code: 'commander.optionMissingArgument'
    });
  }

  /**
   * `Option` does not have a value, and is a mandatory option.
   *
   * @param {Option} option
   * @private
   */

  missingMandatoryOptionValue(option) {
    const message = `error: required option '${option.flags}' not specified`;
    this.error(message, {
      code: 'commander.missingMandatoryOptionValue'
    });
  }

  /**
   * `Option` conflicts with another option.
   *
   * @param {Option} option
   * @param {Option} conflictingOption
   * @private
   */
  _conflictingOption(option, conflictingOption) {
    // The calling code does not know whether a negated option is the source of the
    // value, so do some work to take an educated guess.
    const findBestOptionFromValue = option => {
      const optionKey = option.attributeName();
      const optionValue = this.getOptionValue(optionKey);
      const negativeOption = this.options.find(target => target.negate && optionKey === target.attributeName());
      const positiveOption = this.options.find(target => !target.negate && optionKey === target.attributeName());
      if (negativeOption && (negativeOption.presetArg === undefined && optionValue === false || negativeOption.presetArg !== undefined && optionValue === negativeOption.presetArg)) {
        return negativeOption;
      }
      return positiveOption || option;
    };
    const getErrorMessage = option => {
      const bestOption = findBestOptionFromValue(option);
      const optionKey = bestOption.attributeName();
      const source = this.getOptionValueSource(optionKey);
      if (source === 'env') {
        return `environment variable '${bestOption.envVar}'`;
      }
      return `option '${bestOption.flags}'`;
    };
    const message = `error: ${getErrorMessage(option)} cannot be used with ${getErrorMessage(conflictingOption)}`;
    this.error(message, {
      code: 'commander.conflictingOption'
    });
  }

  /**
   * Unknown option `flag`.
   *
   * @param {string} flag
   * @private
   */

  unknownOption(flag) {
    if (this._allowUnknownOption) return;
    let suggestion = '';
    if (flag.startsWith('--') && this._showSuggestionAfterError) {
      // Looping to pick up the global options too
      let candidateFlags = [];
      // eslint-disable-next-line @typescript-eslint/no-this-alias
      let command = this;
      do {
        const moreFlags = command.createHelp().visibleOptions(command).filter(option => option.long).map(option => option.long);
        candidateFlags = candidateFlags.concat(moreFlags);
        command = command.parent;
      } while (command && !command._enablePositionalOptions);
      suggestion = suggestSimilar(flag, candidateFlags);
    }
    const message = `error: unknown option '${flag}'${suggestion}`;
    this.error(message, {
      code: 'commander.unknownOption'
    });
  }

  /**
   * Excess arguments, more than expected.
   *
   * @param {string[]} receivedArgs
   * @private
   */

  _excessArguments(receivedArgs) {
    if (this._allowExcessArguments) return;
    const expected = this.registeredArguments.length;
    const s = expected === 1 ? '' : 's';
    const forSubcommand = this.parent ? ` for '${this.name()}'` : '';
    const message = `error: too many arguments${forSubcommand}. Expected ${expected} argument${s} but got ${receivedArgs.length}.`;
    this.error(message, {
      code: 'commander.excessArguments'
    });
  }

  /**
   * Unknown command.
   *
   * @private
   */

  unknownCommand() {
    const unknownName = this.args[0];
    let suggestion = '';
    if (this._showSuggestionAfterError) {
      const candidateNames = [];
      this.createHelp().visibleCommands(this).forEach(command => {
        candidateNames.push(command.name());
        // just visible alias
        if (command.alias()) candidateNames.push(command.alias());
      });
      suggestion = suggestSimilar(unknownName, candidateNames);
    }
    const message = `error: unknown command '${unknownName}'${suggestion}`;
    this.error(message, {
      code: 'commander.unknownCommand'
    });
  }

  /**
   * Get or set the program version.
   *
   * This method auto-registers the "-V, --version" option which will print the version number.
   *
   * You can optionally supply the flags and description to override the defaults.
   *
   * @param {string} [str]
   * @param {string} [flags]
   * @param {string} [description]
   * @return {(this | string | undefined)} `this` command for chaining, or version string if no arguments
   */

  version(str, flags, description) {
    if (str === undefined) return this._version;
    this._version = str;
    flags = flags || '-V, --version';
    description = description || 'output the version number';
    const versionOption = this.createOption(flags, description);
    this._versionOptionName = versionOption.attributeName();
    this._registerOption(versionOption);
    this.on('option:' + versionOption.name(), () => {
      this._outputConfiguration.writeOut(`${str}\n`);
      this._exit(0, 'commander.version', str);
    });
    return this;
  }

  /**
   * Set the description.
   *
   * @param {string} [str]
   * @param {object} [argsDescription]
   * @return {(string|Command)}
   */
  description(str, argsDescription) {
    if (str === undefined && argsDescription === undefined) return this._description;
    this._description = str;
    if (argsDescription) {
      this._argsDescription = argsDescription;
    }
    return this;
  }

  /**
   * Set the summary. Used when listed as subcommand of parent.
   *
   * @param {string} [str]
   * @return {(string|Command)}
   */
  summary(str) {
    if (str === undefined) return this._summary;
    this._summary = str;
    return this;
  }

  /**
   * Set an alias for the command.
   *
   * You may call more than once to add multiple aliases. Only the first alias is shown in the auto-generated help.
   *
   * @param {string} [alias]
   * @return {(string|Command)}
   */

  alias(alias) {
    if (alias === undefined) return this._aliases[0]; // just return first, for backwards compatibility

    /** @type {Command} */
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    let command = this;
    if (this.commands.length !== 0 && this.commands[this.commands.length - 1]._executableHandler) {
      // assume adding alias for last added executable subcommand, rather than this
      command = this.commands[this.commands.length - 1];
    }
    if (alias === command._name) throw new Error("Command alias can't be the same as its name");
    const matchingCommand = this.parent?._findCommand(alias);
    if (matchingCommand) {
      // c.f. _registerCommand
      const existingCmd = [matchingCommand.name()].concat(matchingCommand.aliases()).join('|');
      throw new Error(`cannot add alias '${alias}' to command '${this.name()}' as already have command '${existingCmd}'`);
    }
    command._aliases.push(alias);
    return this;
  }

  /**
   * Set aliases for the command.
   *
   * Only the first alias is shown in the auto-generated help.
   *
   * @param {string[]} [aliases]
   * @return {(string[]|Command)}
   */

  aliases(aliases) {
    // Getter for the array of aliases is the main reason for having aliases() in addition to alias().
    if (aliases === undefined) return this._aliases;
    aliases.forEach(alias => this.alias(alias));
    return this;
  }

  /**
   * Set / get the command usage `str`.
   *
   * @param {string} [str]
   * @return {(string|Command)}
   */

  usage(str) {
    if (str === undefined) {
      if (this._usage) return this._usage;
      const args = this.registeredArguments.map(arg => {
        return humanReadableArgName(arg);
      });
      return [].concat(this.options.length || this._helpOption !== null ? '[options]' : [], this.commands.length ? '[command]' : [], this.registeredArguments.length ? args : []).join(' ');
    }
    this._usage = str;
    return this;
  }

  /**
   * Get or set the name of the command.
   *
   * @param {string} [str]
   * @return {(string|Command)}
   */

  name(str) {
    if (str === undefined) return this._name;
    this._name = str;
    return this;
  }

  /**
   * Set the name of the command from script filename, such as process.argv[1],
   * or require.main.filename, or __filename.
   *
   * (Used internally and public although not documented in README.)
   *
   * @example
   * program.nameFromFilename(require.main.filename);
   *
   * @param {string} filename
   * @return {Command}
   */

  nameFromFilename(filename) {
    this._name = path.basename(filename, path.extname(filename));
    return this;
  }

  /**
   * Get or set the directory for searching for executable subcommands of this command.
   *
   * @example
   * program.executableDir(__dirname);
   * // or
   * program.executableDir('subcommands');
   *
   * @param {string} [path]
   * @return {(string|null|Command)}
   */

  executableDir(path) {
    if (path === undefined) return this._executableDir;
    this._executableDir = path;
    return this;
  }

  /**
   * Return program help documentation.
   *
   * @param {{ error: boolean }} [contextOptions] - pass {error:true} to wrap for stderr instead of stdout
   * @return {string}
   */

  helpInformation(contextOptions) {
    const helper = this.createHelp();
    if (helper.helpWidth === undefined) {
      helper.helpWidth = contextOptions && contextOptions.error ? this._outputConfiguration.getErrHelpWidth() : this._outputConfiguration.getOutHelpWidth();
    }
    return helper.formatHelp(this, helper);
  }

  /**
   * @private
   */

  _getHelpContext(contextOptions) {
    contextOptions = contextOptions || {};
    const context = {
      error: !!contextOptions.error
    };
    let write;
    if (context.error) {
      write = arg => this._outputConfiguration.writeErr(arg);
    } else {
      write = arg => this._outputConfiguration.writeOut(arg);
    }
    context.write = contextOptions.write || write;
    context.command = this;
    return context;
  }

  /**
   * Output help information for this command.
   *
   * Outputs built-in help, and custom text added using `.addHelpText()`.
   *
   * @param {{ error: boolean } | Function} [contextOptions] - pass {error:true} to write to stderr instead of stdout
   */

  outputHelp(contextOptions) {
    let deprecatedCallback;
    if (typeof contextOptions === 'function') {
      deprecatedCallback = contextOptions;
      contextOptions = undefined;
    }
    const context = this._getHelpContext(contextOptions);
    this._getCommandAndAncestors().reverse().forEach(command => command.emit('beforeAllHelp', context));
    this.emit('beforeHelp', context);
    let helpInformation = this.helpInformation(context);
    if (deprecatedCallback) {
      helpInformation = deprecatedCallback(helpInformation);
      if (typeof helpInformation !== 'string' && !Buffer.isBuffer(helpInformation)) {
        throw new Error('outputHelp callback must return a string or a Buffer');
      }
    }
    context.write(helpInformation);
    if (this._getHelpOption()?.long) {
      this.emit(this._getHelpOption().long); // deprecated
    }
    this.emit('afterHelp', context);
    this._getCommandAndAncestors().forEach(command => command.emit('afterAllHelp', context));
  }

  /**
   * You can pass in flags and a description to customise the built-in help option.
   * Pass in false to disable the built-in help option.
   *
   * @example
   * program.helpOption('-?, --help' 'show help'); // customise
   * program.helpOption(false); // disable
   *
   * @param {(string | boolean)} flags
   * @param {string} [description]
   * @return {Command} `this` command for chaining
   */

  helpOption(flags, description) {
    // Support disabling built-in help option.
    if (typeof flags === 'boolean') {
      if (flags) {
        this._helpOption = this._helpOption ?? undefined; // preserve existing option
      } else {
        this._helpOption = null; // disable
      }
      return this;
    }

    // Customise flags and description.
    flags = flags ?? '-h, --help';
    description = description ?? 'display help for command';
    this._helpOption = this.createOption(flags, description);
    return this;
  }

  /**
   * Lazy create help option.
   * Returns null if has been disabled with .helpOption(false).
   *
   * @returns {(Option | null)} the help option
   * @package
   */
  _getHelpOption() {
    // Lazy create help option on demand.
    if (this._helpOption === undefined) {
      this.helpOption(undefined, undefined);
    }
    return this._helpOption;
  }

  /**
   * Supply your own option to use for the built-in help option.
   * This is an alternative to using helpOption() to customise the flags and description etc.
   *
   * @param {Option} option
   * @return {Command} `this` command for chaining
   */
  addHelpOption(option) {
    this._helpOption = option;
    return this;
  }

  /**
   * Output help information and exit.
   *
   * Outputs built-in help, and custom text added using `.addHelpText()`.
   *
   * @param {{ error: boolean }} [contextOptions] - pass {error:true} to write to stderr instead of stdout
   */

  help(contextOptions) {
    this.outputHelp(contextOptions);
    let exitCode = process$1.exitCode || 0;
    if (exitCode === 0 && contextOptions && typeof contextOptions !== 'function' && contextOptions.error) {
      exitCode = 1;
    }
    // message: do not have all displayed text available so only passing placeholder.
    this._exit(exitCode, 'commander.help', '(outputHelp)');
  }

  /**
   * Add additional text to be displayed with the built-in help.
   *
   * Position is 'before' or 'after' to affect just this command,
   * and 'beforeAll' or 'afterAll' to affect this command and all its subcommands.
   *
   * @param {string} position - before or after built-in help
   * @param {(string | Function)} text - string to add, or a function returning a string
   * @return {Command} `this` command for chaining
   */
  addHelpText(position, text) {
    const allowedValues = ['beforeAll', 'before', 'after', 'afterAll'];
    if (!allowedValues.includes(position)) {
      throw new Error(`Unexpected value for position to addHelpText.
Expecting one of '${allowedValues.join("', '")}'`);
    }
    const helpEvent = `${position}Help`;
    this.on(helpEvent, context => {
      let helpStr;
      if (typeof text === 'function') {
        helpStr = text({
          error: context.error,
          command: context.command
        });
      } else {
        helpStr = text;
      }
      // Ignore falsy value when nothing to output.
      if (helpStr) {
        context.write(`${helpStr}\n`);
      }
    });
    return this;
  }

  /**
   * Output help information if help flags specified
   *
   * @param {Array} args - array of options to search for help flags
   * @private
   */

  _outputHelpIfRequested(args) {
    const helpOption = this._getHelpOption();
    const helpRequested = helpOption && args.find(arg => helpOption.is(arg));
    if (helpRequested) {
      this.outputHelp();
      // (Do not have all displayed text available so only passing placeholder.)
      this._exit(0, 'commander.helpDisplayed', '(outputHelp)');
    }
  }
};

/**
 * Scan arguments and increment port number for inspect calls (to avoid conflicts when spawning new command).
 *
 * @param {string[]} args - array of arguments from node.execArgv
 * @returns {string[]}
 * @private
 */

function incrementNodeInspectorPort(args) {
  // Testing for these options:
  //  --inspect[=[host:]port]
  //  --inspect-brk[=[host:]port]
  //  --inspect-port=[host:]port
  return args.map(arg => {
    if (!arg.startsWith('--inspect')) {
      return arg;
    }
    let debugOption;
    let debugHost = '127.0.0.1';
    let debugPort = '9229';
    let match;
    if ((match = arg.match(/^(--inspect(-brk)?)$/)) !== null) {
      // e.g. --inspect
      debugOption = match[1];
    } else if ((match = arg.match(/^(--inspect(-brk|-port)?)=([^:]+)$/)) !== null) {
      debugOption = match[1];
      if (/^\d+$/.test(match[3])) {
        // e.g. --inspect=1234
        debugPort = match[3];
      } else {
        // e.g. --inspect=localhost
        debugHost = match[3];
      }
    } else if ((match = arg.match(/^(--inspect(-brk|-port)?)=([^:]+):(\d+)$/)) !== null) {
      // e.g. --inspect=localhost:1234
      debugOption = match[1];
      debugHost = match[3];
      debugPort = match[4];
    }
    if (debugOption && debugPort !== '0') {
      return `${debugOption}=${debugHost}:${parseInt(debugPort) + 1}`;
    }
    return arg;
  });
}
command.Command = Command$2;

const {
  Argument: Argument$1
} = argument;
const {
  Command: Command$1
} = command;
const {
  CommanderError: CommanderError$1,
  InvalidArgumentError: InvalidArgumentError$1
} = error;
const {
  Help: Help$1
} = help;
const {
  Option: Option$1
} = option;
commander.program = new Command$1();
commander.createCommand = name => new Command$1(name);
commander.createOption = (flags, description) => new Option$1(flags, description);
commander.createArgument = (name, description) => new Argument$1(name, description);

/**
 * Expose classes
 */

commander.Command = Command$1;
commander.Option = Option$1;
commander.Argument = Argument$1;
commander.Help = Help$1;
commander.CommanderError = CommanderError$1;
commander.InvalidArgumentError = InvalidArgumentError$1;
commander.InvalidOptionArgumentError = InvalidArgumentError$1; // Deprecated

// wrapper to provide named exports for ESM.
const {
  program,
  createCommand,
  createArgument,
  createOption,
  CommanderError,
  InvalidArgumentError,
  InvalidOptionArgumentError, // deprecated old name
  Command,
  Argument,
  Option,
  Help,
} = commander;

async function checkVersion() {
  return new Promise(async (resolve, reject) => {
    const MirrorList = ["https://jsd.cdn.zzko.cn/gh/NapNeko/NapCatQQ@main/package.json", "https://fastly.jsdelivr.net/gh/NapNeko/NapCatQQ@main/package.json", "https://gcore.jsdelivr.net/gh/NapNeko/NapCatQQ@main/package.json", "https://cdn.jsdelivr.net/gh/NapNeko/NapCatQQ@main/package.json"];
    let version = void 0;
    for (const url of MirrorList) {
      try {
        version = (await RequestUtil.HttpGetJson(url)).version;
      } catch (e) {
        logDebug("检测更新异常", e);
      }
      if (version) {
        resolve(version);
      }
    }
    reject("get verison error!");
  });
}

function _defineProperty$1(e, r, t) {
  return (r = _toPropertyKey$1(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey$1(t) {
  var i = _toPrimitive$1(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive$1(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
class AuthHelper {
  /**
     * 签名凭证方法。
     * @param token 待签名的凭证字符串。
     * @returns 签名后的凭证对象。
     */
  static async signCredential(token) {
    const innerJson = {
      CreatedTime: Date.now(),
      TokenEncoded: token
    };
    const jsonString = JSON.stringify(innerJson);
    const hmac = crypto.createHmac("sha256", AuthHelper.secretKey).update(jsonString, "utf8").digest("hex");
    return {
      Data: innerJson,
      Hmac: hmac
    };
  }
  /**
     * 检查凭证是否被篡改的方法。
     * @param credentialJson 凭证的JSON对象。
     * @returns 布尔值，表示凭证是否有效。
     */
  static async checkCredential(credentialJson) {
    try {
      const jsonString = JSON.stringify(credentialJson.Data);
      const calculatedHmac = crypto.createHmac("sha256", AuthHelper.secretKey).update(jsonString, "utf8").digest("hex");
      return calculatedHmac === credentialJson.Hmac;
    } catch (error) {
      return false;
    }
  }
  /**
     * 验证凭证在1小时内有效且token与原始token相同。
     * @param token 待验证的原始token。
     * @param credentialJson 已签名的凭证JSON对象。
     * @returns 布尔值，表示凭证是否有效且token匹配。
     */
  static async validateCredentialWithinOneHour(token, credentialJson) {
    const isValid = await AuthHelper.checkCredential(credentialJson);
    if (!isValid) {
      return false;
    }
    const currentTime = Date.now() / 1e3;
    const createdTime = credentialJson.Data.CreatedTime;
    const timeDifference = currentTime - createdTime;
    return timeDifference <= 3600 && credentialJson.Data.TokenEncoded === token;
  }
}
_defineProperty$1(AuthHelper, "secretKey", Math.random().toString(36).slice(2));

const LoginRuntime = {
  LoginCurrentTime: Date.now(),
  LoginCurrentRate: 0,
  QQLoginStatus: false,
  //已实现 但太傻了 得去那边注册个回调刷新
  QQQRCodeURL: "",
  QQLoginUin: "",
  NapCatHelper: {
    SetOb11ConfigCall: async (ob11) => {
      return;
    },
    CoreQuickLoginCall: async (uin) => {
      return {
        result: false,
        message: ""
      };
    },
    QQLoginList: []
  }
};
const WebUiDataRuntime = {
  checkLoginRate: async function(RateLimit) {
    LoginRuntime.LoginCurrentRate++;
    if (Date.now() - LoginRuntime.LoginCurrentTime > 1e3 * 60) {
      LoginRuntime.LoginCurrentRate = 0;
      LoginRuntime.LoginCurrentTime = Date.now();
      return true;
    }
    if (LoginRuntime.LoginCurrentRate <= RateLimit) {
      return true;
    }
    return false;
  },
  getQQLoginStatus: async function() {
    return LoginRuntime.QQLoginStatus;
  },
  setQQLoginStatus: async function(status) {
    LoginRuntime.QQLoginStatus = status;
  },
  setQQLoginQrcodeURL: async function(url) {
    LoginRuntime.QQQRCodeURL = url;
  },
  getQQLoginQrcodeURL: async function() {
    return LoginRuntime.QQQRCodeURL;
  },
  setQQLoginUin: async function(uin) {
    LoginRuntime.QQLoginUin = uin;
  },
  getQQLoginUin: async function() {
    return LoginRuntime.QQLoginUin;
  },
  getQQQuickLoginList: async function() {
    return LoginRuntime.NapCatHelper.QQLoginList;
  },
  setQQQuickLoginList: async function(list) {
    LoginRuntime.NapCatHelper.QQLoginList = list;
  },
  setQQQuickLoginCall(func) {
    LoginRuntime.NapCatHelper.CoreQuickLoginCall = func;
  },
  getQQQuickLogin: async function(uin) {
    return await LoginRuntime.NapCatHelper.CoreQuickLoginCall(uin);
  },
  setOB11ConfigCall: async function(func) {
    LoginRuntime.NapCatHelper.SetOb11ConfigCall = func;
  },
  setOB11Config: async function(ob11) {
    await LoginRuntime.NapCatHelper.SetOb11ConfigCall(ob11);
  }
};

const isEmpty$2 = (data) => data === void 0 || data === null || data === "";
const QQGetQRcodeHandler = async (req, res) => {
  if (await WebUiDataRuntime.getQQLoginStatus()) {
    res.send({
      code: -1,
      message: "QQ Is Logined"
    });
    return;
  }
  const qrcodeUrl = await WebUiDataRuntime.getQQLoginQrcodeURL();
  if (isEmpty$2(qrcodeUrl)) {
    res.send({
      code: -1,
      message: "QRCode Get Error"
    });
    return;
  }
  res.send({
    code: 0,
    message: "success",
    data: {
      qrcode: qrcodeUrl
    }
  });
  return;
};
const QQCheckLoginStatusHandler = async (req, res) => {
  res.send({
    code: 0,
    message: "success",
    data: {
      isLogin: await WebUiDataRuntime.getQQLoginStatus()
    }
  });
};
const QQSetQuickLoginHandler = async (req, res) => {
  const {
    uin
  } = req.body;
  const isLogin = await WebUiDataRuntime.getQQLoginStatus();
  if (isLogin) {
    res.send({
      code: -1,
      message: "QQ Is Logined"
    });
    return;
  }
  if (isEmpty$2(uin)) {
    res.send({
      code: -1,
      message: "uin is empty"
    });
    return;
  }
  const {
    result,
    message
  } = await WebUiDataRuntime.getQQQuickLogin(uin);
  if (!result) {
    res.send({
      code: -1,
      message
    });
    return;
  }
  res.send({
    code: 0,
    message: "success"
  });
};
const QQGetQuickLoginListHandler = async (req, res) => {
  const quickLoginList = await WebUiDataRuntime.getQQQuickLoginList();
  res.send({
    code: 0,
    data: quickLoginList
  });
};

const router$3 = Router();
router$3.all("/GetQuickLoginList", QQGetQuickLoginListHandler);
router$3.post("/CheckLoginStatus", QQCheckLoginStatusHandler);
router$3.post("/GetQQLoginQrcode", QQGetQRcodeHandler);
router$3.post("/SetQuickLogin", QQSetQuickLoginHandler);

function _defineProperty(e, r, t) {
  return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e;
}
function _toPropertyKey(t) {
  var i = _toPrimitive(t, "string");
  return "symbol" == typeof i ? i : i + "";
}
function _toPrimitive(t, r) {
  if ("object" != typeof t || !t) return t;
  var e = t[Symbol.toPrimitive];
  if (void 0 !== e) {
    var i = e.call(t, r || "default");
    if ("object" != typeof i) return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return ("string" === r ? String : Number)(t);
}
const __filename$3 = fileURLToPath(import.meta.url);
const __dirname$3 = dirname(__filename$3);
const MAX_PORT_TRY = 100;
async function tryUseHost(host) {
  return new Promise(async (resolve2, reject) => {
    try {
      const server = net.createServer();
      server.on("listening", () => {
        server.close();
        resolve2(host);
      });
      server.on("error", (err) => {
        if (err.code === "EADDRNOTAVAIL") {
          reject("主机地址验证失败，可能为非本机地址");
        } else {
          reject(`遇到错误: ${err.code}`);
        }
      });
      server.listen(0, host);
    } catch (error) {
      reject(`服务器启动时发生错误: ${error}`);
    }
  });
}
async function tryUsePort(port, host, tryCount = 0) {
  return new Promise(async (resolve2, reject) => {
    try {
      const server = net.createServer();
      server.on("listening", () => {
        server.close();
        resolve2(port);
      });
      server.on("error", (err) => {
        if (err.code === "EADDRINUSE") {
          if (tryCount < MAX_PORT_TRY) {
            resolve2(tryUsePort(port + 1, host, tryCount + 1));
          } else {
            reject(`端口尝试失败，达到最大尝试次数: ${MAX_PORT_TRY}`);
          }
        } else {
          reject(`遇到错误: ${err.code}`);
        }
      });
      server.listen(port, host);
    } catch (error) {
      reject(`服务器启动时发生错误: ${error}`);
    }
  });
}
class WebUiConfigWrapper {
  constructor() {
    _defineProperty(this, "WebUiConfigData", void 0);
  }
  applyDefaults(obj, defaults) {
    return {
      ...defaults,
      ...obj
    };
  }
  async GetWebUIConfig() {
    if (this.WebUiConfigData) {
      return this.WebUiConfigData;
    }
    const defaultconfig = {
      host: "0.0.0.0",
      port: 6099,
      prefix: "",
      token: "",
      // 默认先填空，空密码无法登录
      loginRate: 3
    };
    try {
      defaultconfig.token = Math.random().toString(36).slice(2);
    } catch (e) {
      logError("随机密码生成失败", e);
    }
    try {
      const configPath = resolve$3(__dirname$3, "./config/webui.json");
      if (!existsSync(configPath)) {
        writeFileSync(configPath, JSON.stringify(defaultconfig, null, 4));
      }
      const fileContent = readFileSync(configPath, "utf-8");
      const parsedConfig = this.applyDefaults(JSON.parse(fileContent), defaultconfig);
      if (!parsedConfig.prefix.startsWith("/")) parsedConfig.prefix = "/" + parsedConfig.prefix;
      if (parsedConfig.prefix.endsWith("/")) parsedConfig.prefix = parsedConfig.prefix.slice(0, -1);
      writeFileSync(configPath, JSON.stringify(parsedConfig, null, 4));
      const [host_err, host] = await tryUseHost(parsedConfig.host).then((data) => [null, data]).catch((err) => [err, null]);
      if (host_err) {
        logError("host不可用", host_err);
        parsedConfig.port = 0;
      } else {
        parsedConfig.host = host;
        const [port_err, port] = await tryUsePort(parsedConfig.port, parsedConfig.host).then((data) => [null, data]).catch((err) => [err, null]);
        if (port_err) {
          logError("port不可用", port_err);
          parsedConfig.port = 0;
        } else {
          parsedConfig.port = port;
        }
      }
      this.WebUiConfigData = parsedConfig;
      return this.WebUiConfigData;
    } catch (e) {
      logError("读取配置文件失败", e);
    }
    return defaultconfig;
  }
}
const WebUiConfig = new WebUiConfigWrapper();

const isEmpty$1 = (data) => data === void 0 || data === null || data === "";
const LoginHandler = async (req, res) => {
  const WebUiConfigData = await WebUiConfig.GetWebUIConfig();
  const {
    token
  } = req.body;
  if (isEmpty$1(token)) {
    res.json({
      code: -1,
      message: "token is empty"
    });
    return;
  }
  if (!await WebUiDataRuntime.checkLoginRate(WebUiConfigData.loginRate)) {
    res.json({
      code: -1,
      message: "login rate limit"
    });
    return;
  }
  if (WebUiConfigData.token !== token) {
    res.json({
      code: -1,
      message: "token is invalid"
    });
    return;
  }
  const signCredential = Buffer.from(JSON.stringify(await AuthHelper.signCredential(WebUiConfigData.token))).toString("base64");
  res.json({
    code: 0,
    message: "success",
    data: {
      "Credential": signCredential
    }
  });
  return;
};
const LogoutHandler = (req, res) => {
  res.json({
    code: 0,
    message: "success"
  });
  return;
};
const checkHandler = async (req, res) => {
  const WebUiConfigData = await WebUiConfig.GetWebUIConfig();
  const authorization = req.headers.authorization;
  try {
    const CredentialBase64 = authorization?.split(" ")[1];
    const Credential = JSON.parse(Buffer.from(CredentialBase64, "base64").toString());
    await AuthHelper.validateCredentialWithinOneHour(WebUiConfigData.token, Credential);
    res.json({
      code: 0,
      message: "success"
    });
    return;
  } catch (e) {
    res.json({
      code: -1,
      message: "failed"
    });
  }
  return;
};

const router$2 = Router();
router$2.post("/login", LoginHandler);
router$2.post("/check", checkHandler);
router$2.post("/logout", LogoutHandler);

const __filename$2 = fileURLToPath(import.meta.url);
const __dirname$2 = dirname(__filename$2);
const isEmpty = (data) => data === void 0 || data === null || data === "";
const OB11GetConfigHandler = async (req, res) => {
  const isLogin = await WebUiDataRuntime.getQQLoginStatus();
  if (!isLogin) {
    res.send({
      code: -1,
      message: "Not Login"
    });
    return;
  }
  const uin = await WebUiDataRuntime.getQQLoginUin();
  const configFilePath = resolve$3(__dirname$2, `./config/onebot11_${uin}.json`);
  let data;
  try {
    data = JSON.parse(existsSync(configFilePath) ? readFileSync(configFilePath).toString() : readFileSync(resolve$3(__dirname$2, "./config/onebot11.json")).toString());
  } catch (e) {
    data = {};
    res.send({
      code: -1,
      message: "Config Get Error"
    });
    return;
  }
  res.send({
    code: 0,
    message: "success",
    data
  });
  return;
};
const OB11SetConfigHandler = async (req, res) => {
  const isLogin = await WebUiDataRuntime.getQQLoginStatus();
  if (!isLogin) {
    res.send({
      code: -1,
      message: "Not Login"
    });
    return;
  }
  if (isEmpty(req.body.config)) {
    res.send({
      code: -1,
      message: "config is empty"
    });
    return;
  }
  let SetResult;
  try {
    await WebUiDataRuntime.setOB11Config(JSON.parse(req.body.config));
    SetResult = true;
  } catch (e) {
    SetResult = false;
  }
  if (SetResult) {
    res.send({
      code: 0,
      message: "success"
    });
  } else {
    res.send({
      code: -1,
      message: "Config Set Error"
    });
  }
  return;
};

const router$1 = Router();
router$1.post("/GetConfig", OB11GetConfigHandler);
router$1.post("/SetConfig", OB11SetConfigHandler);

const router = Router();
async function AuthApi(req, res, next) {
  if (req.url == "/auth/login") {
    next();
    return;
  }
  if (req.headers?.authorization) {
    const authorization = req.headers.authorization.split(" ");
    if (authorization.length < 2) {
      res.json({
        code: -1,
        msg: "Unauthorized"
      });
      return;
    }
    const token = authorization[1];
    let Credential;
    try {
      Credential = JSON.parse(Buffer.from(token, "base64").toString("utf-8"));
    } catch (e) {
      res.json({
        code: -1,
        msg: "Unauthorized"
      });
      return;
    }
    const config = await WebUiConfig.GetWebUIConfig();
    const credentialJson = await AuthHelper.validateCredentialWithinOneHour(config.token, Credential);
    if (credentialJson) {
      next();
      return;
    }
    res.json({
      code: -1,
      msg: "Unauthorized"
    });
    return;
  }
  res.json({
    code: -1,
    msg: "Server Error"
  });
  return;
}
router.use(AuthApi);
router.all("/test", (req, res) => {
  res.json({
    code: 0,
    msg: "ok"
  });
});
router.use("/auth", router$2);
router.use("/QQLogin", router$3);
router.use("/OB11Config", router$1);

const app = express();
const __filename$1 = fileURLToPath(import.meta.url);
const __dirname$1 = dirname(__filename$1);
async function InitWebUi() {
  const config = await WebUiConfig.GetWebUIConfig();
  if (config.port == 0) {
    log("[NapCat] [WebUi] Current WebUi is not run.");
    return;
  }
  app.use(express.json());
  app.all(config.prefix + "/", (_req, res) => {
    res.json({
      msg: "NapCat WebAPI is now running!"
    });
  });
  app.use(config.prefix + "/webui", express.static(resolve$3(__dirname$1, "./static")));
  app.use(config.prefix + "/api", router);
  app.listen(config.port, config.host, async () => {
    log(`[NapCat] [WebUi] Current WebUi is running at http://${config.host}:${config.port}${config.prefix}`);
    log(`[NapCat] [WebUi] Login URL is http://${config.host}:${config.port}${config.prefix}/webui`);
    log(`[NapCat] [WebUi] Login Token is ${config.token}`);
  });
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const tagColor = chalk.cyan;
program.option("-q, --qq [type]", "QQ号").parse(process.argv);
InitWebUi();
const cmdOptions = program.opts();
checkVersion().then(async (remoteVersion) => {
  const localVersion = JSON.parse(fs$3.readFileSync(path__default.join(__dirname, "package.json")).toString()).version;
  const localVersionList = localVersion.split(".");
  const remoteVersionList = remoteVersion.split(".");
  log(tagColor("[NapCat]"), "当前版本:", localVersion);
  for (const k of [0, 1, 2]) {
    if (parseInt(remoteVersionList[k]) > parseInt(localVersionList[k])) {
      logWarn(tagColor("[NapCat]"), `检测到更新,请前往 https://github.com/NapNeko/NapCatQQ 下载 NapCatQQ V ${remoteVersion}`);
      return;
    } else if (parseInt(remoteVersionList[k]) < parseInt(localVersionList[k])) {
      break;
    }
  }
  logDebug(tagColor("[NapCat]"), "当前已是最新版本");
  return;
}).catch((e) => {
  logError(tagColor("[NapCat]"), "检测更新失败", e);
});
const NapCat_OneBot11 = new NapCatOnebot11();
WebUiDataRuntime.setOB11ConfigCall(NapCat_OneBot11.SetConfig);
napCatCore.onLoginSuccess((uin, uid) => {
  log("登录成功!");
  WebUiDataRuntime.setQQLoginStatus(true);
  WebUiDataRuntime.setQQLoginUin(uin.toString());
});
const showQRCode = async (url, base64, buffer) => {
  await WebUiDataRuntime.setQQLoginQrcodeURL(url);
  logWarn("请扫描下面的二维码，然后在手Q上授权登录：");
  const qrcodePath = path__default.join(__dirname, "qrcode.png");
  qrcode.generate(url, {
    small: true
  }, (res) => {
    logWarn(`
${res}
二维码解码URL: ${url}
如果控制台二维码无法扫码，可以复制解码url到二维码生成网站生成二维码再扫码，也可以打开下方的二维码路径图片进行扫码`);
    fsPromise.writeFile(qrcodePath, buffer).then(() => {
      logWarn("二维码已保存到", qrcodePath);
    });
  });
};
let quickLoginQQ = cmdOptions.qq;
const QuickLoginList = await napCatCore.getQuickLoginList();
if (quickLoginQQ == true) {
  if (QuickLoginList.LocalLoginInfoList.length > 0) {
    quickLoginQQ = QuickLoginList.LocalLoginInfoList[0].uin;
    log("-q 指令指定使用最近的QQ进行快速登录");
  } else {
    quickLoginQQ = "";
  }
}
napCatCore.getQuickLoginList().then((res) => {
  WebUiDataRuntime.setQQQuickLoginList(res.LocalLoginInfoList.filter((item) => item.isQuickLogin).map((item) => item.uin.toString()));
});
WebUiDataRuntime.setQQQuickLoginCall(async (uin) => {
  const QuickLogin = new Promise((resolve, reject) => {
    if (uin) {
      log("正在快速登录 ", uin);
      napCatCore.quickLogin(uin).then((res) => {
        if (res.loginErrorInfo.errMsg) {
          resolve({
            result: false,
            message: res.loginErrorInfo.errMsg
          });
        }
        resolve({
          result: true,
          message: ""
        });
      }).catch((e) => {
        logError(e);
        resolve({
          result: false,
          message: "快速登录发生错误"
        });
      });
    } else {
      resolve({
        result: false,
        message: "快速登录失败"
      });
    }
  });
  const result = await QuickLogin;
  return result;
});
if (quickLoginQQ) {
  log("正在快速登录 ", quickLoginQQ);
  napCatCore.quickLogin(quickLoginQQ).then((res) => {
    if (res.loginErrorInfo.errMsg) {
      logError("快速登录错误:", res.loginErrorInfo.errMsg);
    }
  }).catch((e) => {
    logError("快速登录错误:", e);
    napCatCore.qrLogin(showQRCode);
  });
} else {
  log("没有 -q 指令指定快速登录，将使用二维码登录方式");
  if (QuickLoginList.LocalLoginInfoList.length > 0) {
    log(`可用于快速登录的QQ：${QuickLoginList.LocalLoginInfoList.map((u, index) => `
${index}: ${u.uin} ${u.nickName}`)}`);
  }
  napCatCore.qrLogin(showQRCode);
}
