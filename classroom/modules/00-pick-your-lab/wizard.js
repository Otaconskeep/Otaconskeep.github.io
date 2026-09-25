/* Homelab picker. Side first, then smaller layers, then one build. */
(function (root, factory) {
  var api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.LabWizard = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var FLAVORS = {
    win: {
      name: 'Windows 11 Home',
      build: 'Everyday Windows desk',
      plain: 'The normal PC. A menu, a store, and the games and photo apps people already know.',
      why: 'Windows 11 Home is the outside of the doll. You sit at it. New games expect it. Photo and video apps from the store install without a fight.',
      good: [
        'New games, including many online games that check for cheats.',
        'Photo editing in Lightroom, Photoshop, or the Photos app.',
        'Video editing in DaVinci Resolve or Premiere.',
        'School, mail, and the web.'
      ],
      poor: [
        'A closet box that must stay up for the whole house. Updates can restart Windows.',
        'Many separate little computers inside one machine.'
      ],
      first: [
        'Finish Windows Update before you install your tools.',
        'Put photos and videos on a second disk. Leave the first disk for Windows.',
        'Turn on File History, or copy pictures to a second drive once a week. One disk is not a backup.'
      ],
      next: 'The next doll is Windows 11 Pro if you want Remote Desktop, stronger disk locks, or one practice virtual computer.'
    },
    winpro: {
      name: 'Windows 11 Pro',
      build: 'Windows Pro workbench',
      plain: 'The same Windows desk, with the locks and remote tools a small lab actually uses.',
      why: 'Pro is the layer under Home. You still get games and normal apps. You also get BitLocker, Remote Desktop, and Hyper-V, which is one or two practice computers inside this PC.',
      good: [
        'Everything Home does: games, photos, video, school.',
        'Opening this PC from another computer in the house.',
        'Locking the disk if the computer is stolen.',
        'One practice virtual computer for trying Linux without erasing Windows.'
      ],
      poor: [
        'A big always-on house server. Hyper-V is a practice room, not a building full of guests.',
        'Leaving the PC on a public port. Remote Desktop stays inside the house.'
      ],
      first: [
        'Install Pro, then turn on BitLocker only after you write the recovery key on paper.',
        'Turn on Hyper-V only if you have 16 GB of memory or more. Give the practice computer 4 GB, not half the PC.',
        'Use Remote Desktop from inside the house. Do not forward it to the internet.'
      ],
      next: 'The next doll is a separate Linux closet box when house apps feel cramped inside Windows.'
    },
    mint: {
      name: 'Linux Mint',
      build: 'Friendly Linux desk',
      plain: 'A free Linux desk with a menu and a taskbar. It feels close to Windows.',
      why: 'Mint is the first Linux doll. You can learn files, the terminal, and Docker without throwing away a familiar screen.',
      good: [
        'A daily computer for the web, school, and files.',
        'Free photo tools: digiKam, Darktable, and GIMP.',
        'Free video tools: Kdenlive and Shotcut.',
        'Many Steam games. Indie and older games do well.'
      ],
      poor: [
        'Brand-new online games that require anti-cheat. A lot of those still want Windows.',
        'A tiny always-on appliance.',
        'Splitting one computer into many virtual computers. That is Proxmox, and it wants more memory.'
      ],
      first: [
        'Copy your files somewhere else before you install Mint over a disk.',
        'Learn the file manager first. Then add one Docker app, not ten.',
        'Keep a second copy of photos.'
      ],
      next: 'The next doll is Omarchy, after you can fix a broken update, or Proxmox on a second box when the house needs its own computer.'
    },
    bazzite: {
      name: 'Bazzite',
      build: 'Linux game desk',
      plain: 'A Linux system already set up for Steam, controllers, and graphics cards.',
      why: 'Bazzite is the game doll inside Linux. Universal Blue builds it so Steam and the graphics drivers are part of the plan. You sit at it and play. New anti-cheat games can still refuse to run. Those stay on Windows.',
      good: [
        'A computer you sit at and play on.',
        'Steam, plus many older and indie games.',
        'An NVIDIA card or an AMD card, when you download the matching image.',
        'A normal desk for the web and files between games.'
      ],
      poor: [
        'A closet full of house apps. Movies, backups, and Home Assistant belong on a second computer.',
        'The only copy of family photos.',
        'Brand-new anti-cheat games that only trust Windows.',
        'A first lesson in every Linux command. Bazzite stays in a fixed shape so the game desk does not break.'
      ],
      first: [
        'Download the Desktop image. Pick the NVIDIA image only if the card is NVIDIA.',
        'Copy your files off the disk before you install.',
        'Open Steam after the first boot. That is the point of this doll.'
      ],
      next: 'The next doll is a separate Ubuntu or Proxmox box for movies, backups, and Home Assistant. This computer stays the game desk.'
    },
    omarchy: {
      name: 'Omarchy',
      build: 'Keyboard Linux desk',
      plain: 'Arch Linux already dressed as a keyboard-first desk.',
      why: 'Omarchy is a deeper Linux doll. Arch updates in small bites all the time. The windows sit in a grid and the keyboard drives them. It looks sharp. You are the person who fixes it when an update misbehaves.',
      good: [
        'A daily desk for someone who already fixes Linux problems.',
        'The same free photo and video tools as Mint.',
        'Coding and notes at keyboard speed.',
        'Docker, as a side experiment.'
      ],
      poor: [
        'Your first Linux. Start with Mint.',
        'A closet server. A pretty desk is the wrong shape for a box nobody sits at.',
        'New anti-cheat games. The fancy screen can also fight with normal games.'
      ],
      first: [
        'Read the install notes all the way through before you erase a disk.',
        'Keep a second computer nearby the first week.',
        'Do not put the only copy of family photos here.'
      ],
      next: 'The next doll is a closet computer running Proxmox or Ubuntu. This desk stays the desk.'
    },
    proxmox: {
      name: 'Proxmox',
      build: 'House brain',
      plain: 'A boss computer. You drive it from a web page. It runs many smaller computers inside one real one.',
      why: 'Proxmox is the deep server doll. One guest can be Home Assistant. One can hold movies. One can be a sandbox. If one breaks, the others can keep going. Proxmox is free to use at home. The paid plan is for companies that want a support contract.',
      good: [
        'A closet computer with 32 GB of memory or more.',
        'Snapshots, so a bad experiment can be undone.',
        'Home Assistant, files, and a media server side by side.',
        'A later Windows guest, if memory is left. Games are still happier on a real Windows PC.'
      ],
      poor: [
        '8 or 16 GB of memory. The boss plus the guests will not fit.',
        'The computer you play new games on.',
        'Editing photos in the Proxmox web page. Edit on a desk. Let Proxmox store and serve.'
      ],
      first: [
        'Put Proxmox on its own SSD. Put photos and movies on a different disk.',
        'Leave at least 4 GB of memory for Proxmox itself.',
        'Open the web page only at home. Do not publish it on the internet.'
      ],
      next: 'The next doll is a storage guest such as TrueNAS when the movie or photo pile is the real job, or one guest that owns the graphics card for AI.'
    },
    alpine: {
      name: 'Alpine Linux',
      build: 'Tiny helper',
      plain: 'A very small system for one always-on job.',
      why: 'Alpine is the smallest doll. It uses little memory and little disk. There is no photo desk inside it. You type commands. Pick it when the box is small, you already know Linux, and the job is truly one job.',
      good: [
        'A small always-on helper.',
        'Computers with about 8 GB of memory.',
        'People who can read an error and fix a config file.'
      ],
      poor: [
        'Photo editing, video editing, and games.',
        'Your first Linux.',
        'A pile of random Docker apps. Many of those apps assume Ubuntu or Debian.',
        'Big NVIDIA AI. You would be the mechanic.'
      ],
      first: [
        'Write the one job on paper. A second job means this was the wrong layer.',
        'Keep another computer you can type from.',
        'Update on purpose. Do not forget it for a year.'
      ],
      next: 'The next doll is Ubuntu Server when you want the usual homelab apps without a fight.'
    },
    ubuntu: {
      name: 'Ubuntu Server or Debian',
      build: 'Closet Linux server',
      plain: 'One Linux system that stays on and runs house apps. No fancy desk.',
      why: 'This is the middle server doll. You add Docker and run files, movies, Home Assistant, or a photo library in containers. It is simpler than Proxmox when you only need one system. Most homelab guides assume Ubuntu or Debian, so you will not fight the instructions.',
      good: [
        'A closet server with about 16 GB of memory.',
        'Several house apps in Docker on one system.',
        'Learning real Linux before you learn virtual machines.',
        'Photo libraries such as Immich, if the disks are big enough.'
      ],
      poor: [
        'New anti-cheat games.',
        'Sitting down to edit a wedding video.',
        'Many fully separate computers with snapshots. That wants 32 GB and Proxmox.'
      ],
      first: [
        'Install Ubuntu Server or Debian. Use SSH keys.',
        'Do not open the admin pages to the public internet.',
        'Add one app. Prove you can open it. Then add the next.',
        'Put the system on an SSD. Put movies and photos on a bigger disk.'
      ],
      next: 'The next doll is Proxmox when you have 32 GB and you want each job in its own little computer.'
    },
    mac: {
      name: 'macOS',
      build: 'Mac desk',
      plain: 'The Mac you already sit at. Photos, video, and a quiet kind of local AI.',
      why: 'A Mac is a finished desk. The screen, trackpad, and backups are the product. On Apple silicon, the graphics are not a separate NVIDIA card. They share the Mac’s memory. That memory is called unified memory.',
      good: [
        'Photos and iCloud, and serious edits in Photos or Lightroom.',
        'Video in Final Cut or DaVinci.',
        'Local chat models through Ollama or MLX, sized to the Mac’s memory.',
        'A beautiful daily computer that also starts a small lab habit.'
      ],
      poor: [
        'NVIDIA video cards. Modern macOS does not use them.',
        'Proxmox on the Mac. The Mac is the desk, not the boss of many PC guests.',
        'Every new PC game. Some have no Mac version.'
      ],
      first: [
        'Turn on Time Machine to a disk that is not inside the Mac.',
        'Keep at least a quarter of the memory free. The graphics borrow the same memory as your apps.',
        'Try one local model only after the Mac feels calm in normal use.'
      ],
      next: 'The next doll is a Mac with more unified memory, or a small Linux box beside this Mac for the house.'
    },
    macmini: {
      name: 'Mac mini as a helper',
      build: 'Always-on Mac',
      plain: 'A Mac that stays on for small house jobs. You still drive it from another screen.',
      why: 'A Mac mini is a quiet closet doll. It can share files, run a few containers, and host a small smart-home helper. It will not become a stack of virtual PCs, and it will not grow an NVIDIA card.',
      good: [
        'Files, Time Machine targets, and a small Docker or OrbStack setup.',
        'Homebridge or a light Home Assistant helper.',
        'Small chat models if the mini has 16 GB of unified memory or more.',
        'A box that sips power and stays quiet.'
      ],
      poor: [
        'A movie fortress with many huge disks and a graphics card for AI video.',
        'Proxmox-style guests.',
        'Editing the family video on the mini while it is also the server. Edit on a desk Mac.'
      ],
      first: [
        'Turn on Remote Login for yourself. Do not expose it to the internet.',
        'Plug the big file disk into the mini. Keep macOS on the internal drive.',
        'Add one house app. Stop there until it has behaved for a week.'
      ],
      next: 'The next doll is a real Linux server when you want Proxmox, a graphics card, or a large movie pile.'
    },
    maclab: {
      name: 'Mac desk plus a lab box',
      build: 'Mac desk and a small lab',
      plain: 'The Mac stays the computer you love. A second, cheaper computer runs the house.',
      why: 'This is two dolls that fit together. The Mac edits photos and video and stays pretty. The lab box stays on, runs Docker or Proxmox, and takes the jobs that would make the Mac feel like a server.',
      good: [
        'Final Cut, Photos, and daily Mac life with no compromise.',
        'A house server that can restart without taking your desk down.',
        'A clear place for movies, backups, and Home Assistant.',
        'A later graphics card, on the lab box, if you want local AI video.'
      ],
      poor: [
        'Trying to make the Mac itself into Proxmox.',
        'Buying a huge GPU for the Mac. Put that money in the lab box.',
        'One disk holding the only copy of both machines’ files.'
      ],
      first: [
        'Leave the Mac as it is. Do not erase it to “make a server.”',
        'Buy or reuse a small PC for the lab. 16 GB runs Ubuntu. 32 GB or more can run Proxmox.',
        'Point Time Machine at a disk on the lab box, and keep a second copy of photos off site if you can.'
      ],
      next: 'When the lab box has 32 GB, move it from Ubuntu to Proxmox. The Mac does not change.'
    }
  };

  var RAM_TEXT = {
    8: '8 GB is one job at a time. A normal desk can work. Do not run several pretend computers. Do not run a big AI model.',
    16: '16 GB is a solid daily computer or a starter closet server. A couple of small house apps can share it. Proxmox with many guests will feel cramped.',
    32: '32 GB is where a real lab starts. Proxmox can hold a few guests. A Windows guest still wants about 8 GB, so do not give every guest a feast.',
    64: '64 GB is a comfortable lab. A heavier guest, Home Assistant, and a media app can all stay up.',
    128: '128 GB is a big lab. Many services can stay up. A large AI model can sit in normal memory, but it is still slow if a graphics card is not doing the work.'
  };

  var MAC_RAM_TEXT = {
    8: '8 GB of unified memory is tight on a modern Mac. The screen and the graphics share it. You can write and browse. A local AI model will push the Mac into swapping, which means it uses the disk as fake memory and feels sticky.',
    16: '16 GB is the calm daily Mac. Photos and a normal edit fit. A small chat model can run, and it shares this same 16 GB with everything else you have open. Close big apps first.',
    24: '24 GB gives photo and video work more air. Mid-size local models become reasonable if you are not exporting a video at the same time.',
    32: '32 GB is a strong Mac for Final Cut and for local models. The graphics still borrow this pool. Leave headroom.',
    64: '64 GB is a serious Apple-silicon workstation. Larger local models fit. NVIDIA-style AI video still belongs on a PC graphics card, not in this pool.',
    128: '128 GB of unified memory is a top Mac. Big local models fit. It is still not a stack of Proxmox guests, and it is still not an NVIDIA video card.'
  };

  var GPU_TEXT = {
    none: {
      label: 'No extra graphics card',
      games: 'Fine for the web and for watching videos. New 3D games will struggle.',
      photos: 'You can sort photos and do light edits. Huge camera files with heavy filters will feel slow.',
      video: 'Short 1080p edits can work. 4K editing will hurt. AI video is not for this computer.',
      models: 'Only very small chat models, about 1 to 3 billion parameters, on the processor. A parameter is one note the model memorized. Answers will be slow. This is practice AI, not a daily assistant.'
    },
    1: {
      label: 'About 1 GB graphics card, or smaller',
      games: 'This is a very old card. It can show the desktop and play very old games. New 3D games will not run well.',
      photos: 'You can look through photos. Heavy filters and huge camera files will feel slow.',
      video: 'Watching a video can work. Editing will hurt. AI video does not fit on 1 GB.',
      models: '1 GB is too small to hold a chat model on the card. A tiny model can still run on the processor, and it will be slow. This is not a daily AI computer.'
    },
    2: {
      label: 'About 2 GB graphics card',
      games: 'Old games at low settings can work. New games will struggle, or they will not start.',
      photos: 'Light photo edits fit. Heavy filters will feel slow.',
      video: 'A short 1080p clip can be tried. 4K editing and AI video do not fit.',
      models: '2 GB cannot hold a useful chat model. A 7-billion-parameter model needs several times this much card memory. A tiny practice model can use the processor instead, and it will be slow.'
    },
    4: {
      label: 'About 3 or 4 GB graphics card',
      games: 'Older games at 1080p can work if you turn the settings down. New games want more card memory.',
      photos: 'Normal photo edits fit. Huge files with many filters will still feel slow.',
      video: '1080p editing can be tried. 4K editing and AI video do not fit.',
      models: 'A tiny chat model can try this card. A 7-billion-parameter model does not fit once the conversation memory is counted. That model wants a bigger card.'
    },
    6: {
      label: 'About 6 GB graphics card',
      games: 'Older games and many current games at 1080p. Turn some settings down.',
      photos: 'Real photo editing is fine.',
      video: '1080p editing is fine. 4K is tight. AI video clips do not fit well.',
      models: 'A 7-billion-parameter chat model, in a smaller 4-bit copy, fits. A 4-bit copy uses less memory and is a little less sharp. A small Whisper hearing model fits. A 14-billion chat model is too big to feel good.'
    },
    8: {
      label: 'About 8 GB graphics card',
      games: '1080p is the sweet spot. Some 1440p if you lower settings.',
      photos: 'Photo editing is comfortable.',
      video: '1080p is comfortable. 4K can work if you edit with small stand-in clips. AI video is still a poor fit.',
      models: '7 to 8 billion parameter models fit well in a 4-bit copy. Older picture models fit. The larger SDXL picture model is tight and slow.'
    },
    12: {
      label: 'About 12 GB graphics card',
      games: '1080p is easy. 1440p is reasonable for many games.',
      photos: 'Heavier photo files are comfortable.',
      video: '4K editing becomes reasonable. Short AI video can start, and it will be slow.',
      models: 'About a 14-billion-parameter chat model fits in a 4-bit copy. Run one heavy job at a time. Do not game and run a model together.'
    },
    16: {
      label: 'About 16 GB graphics card',
      games: '1440p is realistic for many new games.',
      photos: 'Heavy photo work is fine.',
      video: '4K editing is a fair daily job. Some short AI video workflows fit.',
      models: '14-billion chat models fit more comfortably. A 32-billion model is still tight. A 70-billion model does not belong here.'
    },
    24: {
      label: 'About 24 GB graphics card',
      games: 'High settings at 1440p, and 4K in many games.',
      photos: 'The card is not the limit for photos.',
      video: '4K editing is comfortable. Local AI video becomes a real experiment: short clips, not a movie studio.',
      models: 'About a 32-billion-parameter chat model can fit in a 4-bit copy. Picture models fit. A 70-billion model still wants more, or it borrows normal RAM and gets slow.'
    }
  };

  var STORAGE_TEXT = {
    256: '256 GB holds the system and some apps. It does not hold a family photo vault or a movie library.',
    1000: '1 TB holds the system, a pile of games, or a starter photo library. Phone photos fit for a while. Years of 4K video do not.',
    4000: '4 TB is a real photo library or a small movie shelf. One disk can die. A backup is a second copy. One disk is not a backup.',
    8000: '8 TB is a family movie library or a big camera archive. Put the system on a fast SSD. Put the pile on a hard drive.',
    16000: '16 TB or more is media-server size. Use more than one disk. A mirror protects you from one disk dying. It does not protect you from fire, theft, or a mistaken delete.'
  };

  var BUDGET_TEXT = {
    have: 'You already own the computer. This build uses the parts you named. It does not sneak in a graphics card or a pile of memory you do not have.',
    200: 'Under $200 is a used small office PC, or the computer you already own. It can be a tiny server. It is not a new gaming PC and it will not run big AI models.',
    500: '$200 to $500 can buy a used office PC with 16 to 32 GB, or a mini PC. That is a good closet server. A strong graphics card is luck, not the plan.',
    1200: '$500 to $1,200 can be a starter lab with about 32 GB and a used graphics card, or a nice daily PC. Games plus a full server usually means this money buys one strong role, not both at full strength.',
    more: 'More than $1,200 can be two machines. That is the calm plan: one daily computer, and one closet server.'
  };

  var JOB_LABELS = {
    games: 'Games',
    photos: 'Photos',
    video: 'Video',
    movies: 'Movies and TV',
    smart: 'Smart home',
    ai: 'Local AI',
    learn: 'Learning',
    files: 'Files and backups'
  };

  function jobList(a) {
    if (!a || a.job == null || a.job === '') return [];
    return Array.isArray(a.job) ? a.job.slice() : [a.job];
  }

  function hasJob(a, id) {
    return jobList(a).indexOf(id) !== -1;
  }

  function flavorChoices(a) {
    var out = [];
    function add(id) {
      var item = FLAVORS[id];
      out.push({ value: id, label: item.name, detail: item.plain });
    }
    if (a.side === 'win') {
      add('win');
      add('winpro');
      return out;
    }
    if (a.side === 'mac') {
      if (a.role === 'server') {
        add('macmini');
        return out;
      }
      add('mac');
      if (a.role === 'both' || a.skill === 'lab') add('maclab');
      if (a.role === 'everyday' && a.skill !== 'lab') add('macmini');
      return out;
    }
    if (a.role !== 'server' && hasJob(a, 'games')) add('bazzite');
    if (a.role !== 'server') add('mint');
    if (a.role !== 'server' && a.skill === 'ok') add('omarchy');
    if (a.role !== 'everyday') {
      add('ubuntu');
      if (Number(a.ram) >= 32) add('proxmox');
      var jobs = jobList(a);
      var onlySmallJobs = jobs.length > 0 && jobs.every(function (id) { return id === 'smart' || id === 'learn'; });
      if (Number(a.ram) <= 8 && a.skill === 'ok' && onlySmallJobs) add('alpine');
    }
    if (!out.length) add('mint');
    return out;
  }

  function explain(answers) {
    var a = answers || {};
    var choices = flavorChoices(a);
    var allowed = {};
    choices.forEach(function (choice) { allowed[choice.value] = true; });
    var pick = allowed[a.flavor] ? a.flavor : choices[0].value;
    var profile = FLAVORS[pick];
    var mac = a.side === 'mac' && pick !== 'maclab';
    var gpu = GPU_TEXT[a.gpu] || GPU_TEXT.none;
    var ramLine = (a.side === 'mac' ? MAC_RAM_TEXT : RAM_TEXT)[Number(a.ram)] || RAM_TEXT[16];
    var storage = STORAGE_TEXT[Number(a.storage)] || STORAGE_TEXT[256];
    if ((hasJob(a, 'movies') || hasJob(a, 'files') || hasJob(a, 'photos')) && Number(a.storage) >= 4000 && a.role !== 'everyday' && pick !== 'mac') {
      storage += ' If the pile is the real job, TrueNAS can be the shelf. It is free. Unraid does a similar job and costs money. The shelf keeps disks. It is not your game desk.';
    }
    var labLine = '';
    if (pick === 'maclab') {
      labLine = Number(a.ram) >= 32
        ? 'The lab box in this build is Proxmox, because 32 GB or more was on the table. The Mac stays macOS.'
        : 'The lab box in this build is Ubuntu Server or Debian. Step up to Proxmox only after that box has 32 GB.';
    }
    var pickedJobs = jobList(a).map(function (id) { return JOB_LABELS[id] || id; });
    return {
      pick: pick,
      choices: choices,
      jobs: pickedJobs,
      plan: buildPlan(a, pick),
      because: profile.why,
      profile: profile,
      labLine: labLine,
      hardware: {
        ram: ramLine,
        gpuLabel: mac ? 'Unified memory, shared with the graphics' : gpu.label,
        games: mac
          ? 'Mac games exist. Some big PC games have no Mac version, and anti-cheat games often do not show up here.'
          : gpu.games,
        photos: mac
          ? 'Photos and Lightroom fit a Mac well. ' + (gpu.photos ? '' : '') + 'Heavy jobs still need free unified memory, because the graphics borrow it.'
          : gpu.photos,
        video: mac
          ? 'Final Cut and DaVinci are the video path. AI video that expects an NVIDIA card does not move onto a Mac. Short experiments exist. A movie pipeline does not.'
          : gpu.video,
        models: mac
          ? macModels(Number(a.ram))
          : gpu.models,
        storage: storage,
        budget: BUDGET_TEXT[a.budget] || BUDGET_TEXT.have
      },
      others: choices.filter(function (choice) { return choice.value !== pick; }).map(function (choice) {
        return { name: FLAVORS[choice.value].name, plain: FLAVORS[choice.value].plain };
      })
    };
  }

  function gpuGb(a) {
    if (!a || a.side === 'mac' || a.gpu === 'none' || a.gpu == null || a.gpu === '') return 0;
    var n = Number(a.gpu);
    return n > 0 ? n : 0;
  }

  function buildPlan(a, pick) {
    var ram = Number(a.ram) || 16;
    var card = gpuGb(a);
    var disk = Number(a.storage) || 0;
    var server = pick === 'proxmox' || pick === 'ubuntu' || pick === 'alpine' || pick === 'macmini';
    var desk = pick === 'win' || pick === 'winpro' || pick === 'mint' || pick === 'bazzite' || pick === 'omarchy' || pick === 'mac';
    var now = [];
    var later = [];
    function add(list, name, detail) { list.push(name + '. ' + detail); }
    function ollamaReady() {
      if (a.side === 'mac' || pick === 'mac' || pick === 'macmini') return ram >= 16;
      if (card >= 6) return true;
      return ram >= 32 && card === 0;
    }

    var use = '';
    var setup = [];
    if (pick === 'win' || pick === 'winpro') {
      use = 'Use Windows 11. Download it from Microsoft. When the installer asks for a product key, choose I don’t have a product key. Windows runs without activation. A small watermark can sit on the screen, and some wallpaper settings stay locked until you buy a real key from Microsoft. You do not need a borrowed key.';
      setup = [
        'Use Microsoft’s own Windows 11 installer.',
        'On the product-key screen, choose I don’t have a product key.',
        'Finish Windows Update before you add Steam or house apps.',
        'Put games and photos on a second disk when you have one. Leave the first disk for Windows.'
      ];
      if (pick === 'winpro') {
        setup.push('Pro adds BitLocker, Remote Desktop, and Hyper-V. Write the BitLocker recovery key on paper before you turn BitLocker on. Use Remote Desktop only inside the house.');
      }
    } else if (pick === 'bazzite') {
      use = 'Use Bazzite. It is a Linux game desk with Steam already in the plan. Download the Desktop image. Pick the NVIDIA download only if your card is NVIDIA. AMD and Intel graphics use the other image.';
      setup = [
        'Copy your files off the target disk first.',
        'Write the Bazzite image to a USB and install it.',
        'Open Steam after the first boot and sign in.',
        'Keep movies, backups, and Home Assistant on a second computer if you have one. This one is the game desk.'
      ];
    } else if (pick === 'mint') {
      use = hasJob(a, 'games')
        ? 'You can install Linux Mint Cinnamon for a familiar desk. If games are the main job, use Bazzite instead. Bazzite already includes the game setup. Mint is the better doll when you want to learn the normal Linux desk.'
        : 'Use Linux Mint Cinnamon. Download it from the Linux Mint site. It is the friendly desk, with a menu and a taskbar.';
      setup = [
        'Write Mint to a USB. Keep your old files on another disk until the new desk is open.',
        'Add programs from the Software Manager first.',
        'Add one extra tool. Use it for a week before you add another.'
      ];
    } else if (pick === 'omarchy') {
      use = 'Use Omarchy. It is a good daily Linux desk: Arch, already set up, keyboard first. Pick it when you can fix an update. It is a poor first Linux and a poor closet server. New anti-cheat games still want Windows or Bazzite.';
      setup = [
        'Read the install notes on the Omarchy site before you erase a disk.',
        'Keep a second computer nearby for the first week.',
        'Do not put the only copy of family photos here.',
        'Add Ollama from Ollama’s own download if you want a local model. The OtaconsKeep Lite installer is not written for Arch.'
      ];
    } else if (pick === 'proxmox') {
      use = 'Use Proxmox VE. It is free for a home. You drive it from a web page in the house. Each job gets its own small computer, called a guest. The host is Proxmox itself, and it must keep some memory.';
      setup = ram >= 64
        ? [
          'Install Proxmox VE on its own SSD. Leave the big disks for files and movies.',
          'Leave 8 GB of memory for the Proxmox host. Do not give that 8 GB to guests.',
          'Start with the guests that match your jobs. A movie guest gets 4 GB. A smart-home guest gets 4 GB. A files guest gets 4 GB.',
          'Give the graphics card to one guest only, and only if that guest runs AI. The other guests use the processor.',
          'Open the Proxmox web page only from inside the house. Add one guest, prove it opens, then add the next.'
        ]
        : [
          'Install Proxmox VE on its own SSD. Leave the big disks for files and movies.',
          'Leave 4 GB of memory for the Proxmox host.',
          'Start with two guests. Give each one 4 GB. A 32 GB machine cannot hold a crowd.',
          'Give the graphics card to one guest only, and only if that guest runs AI.',
          'Open the Proxmox web page only from inside the house.'
        ];
    } else if (pick === 'ubuntu') {
      use = 'Use Ubuntu Server LTS. LTS means this edition stays supported for years. Install Docker, then add house apps one at a time. Most homelab instructions assume Ubuntu, so you will not fight the guide.';
      setup = [
        'Install Ubuntu Server LTS and turn on SSH so you can control it from another computer.',
        'Install Docker Engine using Docker’s Ubuntu instructions.',
        'Add one app. Open it from another computer in the house. Then add the next.',
        'Keep the admin pages off the public internet.',
        'Put Ubuntu on an SSD. Put movies and photos on a bigger disk.'
      ];
    } else if (pick === 'alpine') {
      use = 'Use Alpine for one job only. It is small on purpose. A second app means this was the wrong system. Ubuntu Server is the stack doll.';
      setup = [
        'Write the one job on paper before you install.',
        'Keep another computer you can type from.',
        'Do not add a pile of Docker apps here. Many of them assume Ubuntu.'
      ];
    } else if (pick === 'mac' || pick === 'macmini') {
      use = pick === 'mac'
        ? 'Stay on macOS. Do not erase the Mac to build a server. Add one house helper only after normal Mac life feels calm.'
        : 'Use the Mac mini as the always-on helper. Leave macOS on the internal drive. Plug the big file disk in beside it.';
      setup = [
        'Turn on Time Machine to a disk that is not the only copy of your photos.',
        'Turn on Remote Login for yourself. Do not open it to the public internet.',
        'Add one app. Leave it alone for a week before you add another.'
      ];
    } else if (pick === 'maclab') {
      use = ram >= 32
        ? 'Keep the Mac on macOS. The second computer should be Proxmox, because 32 GB or more was on the table. Edit on the Mac. Run the house on the lab box.'
        : 'Keep the Mac on macOS. The second computer should be Ubuntu Server until it has 32 GB. Then it can become Proxmox. Edit on the Mac. Run the house on the lab box.';
      setup = [
        'Do not erase the Mac.',
        'Install the lab system on the other computer.',
        'Point Time Machine at a disk on the lab box, and keep another copy of photos somewhere else.'
      ];
    }

    if (hasJob(a, 'games')) {
      if (pick === 'bazzite' || pick === 'win' || pick === 'winpro' || pick === 'mac') {
        add(now, 'Steam', pick === 'mac'
          ? 'Install Steam from the Mac App Store or the Steam site. Some big PC games have no Mac version.'
          : 'Install Steam and play here. New anti-cheat games are most at home on Windows.');
      } else if (pick === 'mint') {
        add(now, 'Steam', 'Mint can run many Steam games. If the game library is the real job, switch this desk to Bazzite.');
      } else {
        add(later, 'A game desk', 'This computer should not be the game machine. Play on Windows, or on a Linux desk called Bazzite. Leave this box for the house.');
      }
    }

    if (hasJob(a, 'movies') || (server && disk >= 4000)) {
      var movieWhere = server || pick === 'maclab' || pick === 'macmini' ? now : later;
      if (hasJob(a, 'movies') && desk && pick !== 'bazzite') movieWhere = now;
      if (pick === 'bazzite') movieWhere = later;
      add(movieWhere, 'Jellyfin or Plex', card > 0 && card <= 2
        ? 'Either one can serve movies to the TVs in the house. A 1 or 2 GB card often cannot convert video for a phone. Play the original file, or let the TV do that work. Start with one of these apps, not both.'
        : 'Either one can serve movies and TV to the house. Jellyfin is free. Plex is the other famous choice and has paid extras. Start with one, not both. The computer that runs it has to stay on.');
    } else if (server || pick === 'maclab') {
      add(later, 'Jellyfin or Plex', 'When the movie pile shows up, one of these becomes the house player. Jellyfin is free. Plex is the paid-extras choice. A few terabytes of disk makes this real.');
    }

    if (hasJob(a, 'photos')) {
      if (pick === 'win' || pick === 'winpro' || pick === 'mac' || pick === 'maclab') {
        add(now, 'Photos or Lightroom', 'Edit on the desk you sit at. Keep the library on a second disk.');
      } else if (pick === 'mint' || pick === 'bazzite' || pick === 'omarchy') {
        add(now, 'digiKam or Darktable', 'These are the free photo desks. Edit here. Store the pile on a second disk.');
      }
      if (server || pick === 'macmini' || pick === 'maclab' || disk >= 4000) {
        add(disk >= 1000 ? now : later, 'Immich', 'Immich is a private photo library for the whole house, like a photo cloud you own. It wants a big disk and a computer that stays on.');
      }
    } else if (server && disk >= 4000) {
      add(later, 'Immich', 'Immich can hold the family photo library in the house when you are ready. It is not a public cloud.');
    }

    if (hasJob(a, 'video') && (desk || pick === 'maclab' || pick === 'win' || pick === 'winpro')) {
      add(now, pick === 'mac' || pick === 'maclab' ? 'Final Cut or DaVinci' : 'DaVinci Resolve or Kdenlive', 'Edit on the desk. Let a server store the footage if you add one later. Do not edit the movie inside Proxmox.');
    }

    if (hasJob(a, 'smart') || server || pick === 'maclab') {
      var smartList = hasJob(a, 'smart') && pick !== 'alpine' ? now : (hasJob(a, 'smart') ? now : later);
      if (pick === 'bazzite' || ((pick === 'win' || pick === 'mint' || pick === 'omarchy' || pick === 'mac') && a.role === 'everyday')) {
        smartList = later;
      }
      add(smartList, 'Home Assistant', pick === 'alpine'
        ? 'This can be the one Alpine job. It runs lights, sensors, and switches. Do not add a second app beside it.'
        : (pick === 'proxmox' || pick === 'maclab'
          ? 'Home Assistant runs the lights and sensors. Give it a 4 GB guest of its own. Keep its page inside the house.'
          : 'Home Assistant runs the lights and sensors. Install it with Docker. Keep its page inside the house.'));
    }

    if (hasJob(a, 'ai') || card >= 6 || ((a.side === 'mac' || pick === 'mac' || pick === 'macmini') && ram >= 16)) {
      var aiNow = hasJob(a, 'ai') && ollamaReady() && pick !== 'alpine';
      var aiDetail = 'Ollama is how a house runs its own chat model. This card or this amount of memory is too small for a useful one. The install waits for a bigger card, or for 32 GB and a lot of patience.';
      if (ollamaReady() && card >= 6 && pick === 'proxmox') {
        aiDetail = 'Ollama runs a chat model here. Put it in the one guest that owns the graphics card. Run one model at a time.';
      } else if (ollamaReady() && card >= 6) {
        aiDetail = 'Ollama runs a chat model on the graphics card. Run one model at a time, and close heavy games or a video export first.';
      } else if (ollamaReady() && (a.side === 'mac' || pick === 'mac' || pick === 'macmini')) {
        aiDetail = 'Ollama runs a chat model in the Mac’s unified memory. Close big apps first. Run one model at a time.';
      } else if (ollamaReady()) {
        aiDetail = 'Ollama can run a small model on the processor. It will be slow. This is practice, not a daily assistant.';
      }
      add(aiNow ? now : later, 'Ollama', aiDetail);
    }

    if (hasJob(a, 'files') || (server && disk >= 4000) || pick === 'maclab') {
      add(hasJob(a, 'files') || disk >= 4000 ? now : later, 'A shared folder', pick === 'proxmox'
        ? 'Give one guest the big disks and share a folder with the rest of the house. TrueNAS can be that guest when the pile is huge. A shared folder is not a backup. Keep a second copy somewhere else.'
        : 'Share one folder with the other computers in the house. Samba does this on Linux. A Mac can share a folder too. One disk is still not a backup.');
    }

    if (hasJob(a, 'learn') && !now.length) {
      add(now, 'One practice app', 'Learn this system with a single app. A web page you can open from another computer is enough for week one.');
    }

    if (pick === 'alpine' && now.length > 1) {
      later = now.slice(1).concat(later);
      now = [now[0]];
      later.unshift('One job only. Alpine stays small. Move the rest of this list to Ubuntu Server when you want more than one app.');
    }

    var built = buildGuide(a, pick, ram, card);
    return {
      use: use,
      setup: setup,
      now: now,
      later: later,
      path: built.path,
      keep: built.keep,
      guides: built.guides,
      lessons: built.lessons,
      advanced: built.advanced
    };
  }

  function buildGuide(a, pick, ram, card) {
    var guides = [];
    var lessons = [];
    var liteMachine = pick === 'win' || pick === 'winpro' || pick === 'ubuntu';
    var wantsMedia = hasJob(a, 'movies') || pick === 'proxmox' || pick === 'ubuntu' || pick === 'maclab';
    var path = [
      'Install the system from Use this. Sign in. Restart once. If it comes back, the computer is ready for apps.',
      'Read the lessons below in order. Each lesson is one service. Finish the "done looks like" line before you start the next service.',
      'Keep every admin page inside the house. A page that manages files, movies, or the Keep should not be open to the public internet.'
    ];
    var keep = '';

    if (liteMachine) {
      keep = 'OtaconsKeep Lite fits this computer. It is free. The installer sets up the Keep, Ollama, and Piper voice for the agents. Premium is a one-dollar seat after Lite already works. Premium adds the five-agent crew and Video Studio. Premium does not install Plex, Sonarr, Radarr, or Prowlarr.';
      if (card > 0 && card <= 2) keep += ' A 1 or 2 GB card can still run Lite, with a very small chat model. Video Studio wants a bigger card.';
      else if (card > 2 && card < 6) keep += ' A 3 or 4 GB card can still run Lite, with a very small chat model. Video Studio wants a bigger card.';
      path.push('Install OtaconsKeep Lite. On Windows, download Setup from the Lite page and watch the install video once. On Ubuntu Server, use the Ubuntu steps on that same page. When it says ready, open localhost:5757 on that computer.');
      path.push('Add Premium only after Lite works, and only if you want the larger crew or Video Studio.');
    } else if (pick === 'mint') {
      keep = 'OtaconsKeep Lite’s Linux installer is written for Ubuntu or Debian. Mint can follow the Ubuntu steps on the Lite page. If a step does not match, stop and use Ollama’s own download. Premium does not install Plex or the arr apps.';
      path.push('Try OtaconsKeep Lite from the Ubuntu steps on the Lite page. If the steps assume Ubuntu and yours do not match, install Ollama from Ollama’s download page instead.');
    } else if (pick === 'proxmox' || pick === 'maclab') {
      keep = 'Do not install OtaconsKeep Lite on the Proxmox host. Install Lite on the Windows computer you sit at, or inside an Ubuntu guest. Lite brings Ollama and Piper for the agents. Plex and the arr apps are separate. Premium does not install them.';
      path.push('Leave the Proxmox host as the boss. Install OtaconsKeep Lite on your Windows desk, or in one Ubuntu guest, when you want the Keep’s Ollama and Piper.');
    } else if (pick === 'mac' || pick === 'macmini') {
      keep = 'OtaconsKeep Lite’s installer is Windows, plus Ubuntu or Debian. It is not a Mac installer. On this Mac, install Ollama from Ollama’s download page. House Piper is the classroom voice lesson. Premium does not install Plex or the arr apps.';
      path.push('Install Ollama from Ollama’s Mac download. Lite will not set this Mac up for you.');
    } else if (pick === 'bazzite') {
      keep = 'Bazzite is the game desk. OtaconsKeep Lite targets Windows and Ubuntu or Debian, not Bazzite. Install Ollama from Ollama’s site if you want a local model here. Put Lite on a Windows or Ubuntu computer when you want the Keep’s Piper voice. Premium does not install Plex or the arr apps.';
      path.push('Open Steam first, from the Bazzite setup above. Add Ollama from Ollama’s download only after games already launch.');
    } else if (pick === 'omarchy') {
      keep = 'Omarchy is a good daily Linux desk. Lite’s installer is not written for Arch, so do not force that setup script onto Omarchy. Use Ollama’s download for the chat model. Use Piper’s project and Classroom Module 4 for voice. Premium does not install Plex or the arr apps.';
      path.push('Install Omarchy from its own site. Then add Ollama from Ollama’s download. Do not run the OtaconsKeep Lite installer here.');
    } else if (pick === 'alpine') {
      keep = 'Alpine is one small job. OtaconsKeep Lite, Plex, and the arr stack are too many apps for this box. Put that stack on Ubuntu Server. The guides below are for that next computer.';
      path.push('Give Alpine the one job you wrote down. Stop there.');
    } else {
      keep = 'OtaconsKeep Lite installs Ollama and Piper on Windows and on Ubuntu or Debian. It does not install Plex or the arr apps. Premium does not install them either.';
    }

    if (wantsMedia || hasJob(a, 'movies')) {
      path.push('Install Jellyfin or Plex yourself and play one video on a TV in the house. OtaconsKeep Lite will not install this. Premium will not install it either.');
      path.push('Then add the arr apps in this order: Prowlarr, Sonarr, Radarr. One app, prove it opens, then the next. Classroom Module 10 walks the Sonarr and Radarr part.');
    } else {
      path.push('When you want movies, install Jellyfin or Plex yourself, play one video, then add Prowlarr, Sonarr, and Radarr. Lite and Premium do not install those.');
    }

    if (hasJob(a, 'smart') || pick === 'proxmox' || pick === 'ubuntu') {
      path.push('Install Home Assistant only after the machine is calm. Keep its page inside the house. The Home Assistant lesson below is the longer version.');
    }

    path.push('Add one service. Open it from another computer in the house. Then add the next.');
    lessons = serviceLessons(a, pick, ram, card, liteMachine);
    var advanced = advancedLayer(a, pick, ram, card);
    lessons.forEach(function (item) {
      (item.links || []).forEach(function (link) { guides.push(link); });
    });
    advanced.forEach(function (item) {
      (item.links || []).forEach(function (link) { guides.push(link); });
    });
    return { path: path, keep: keep, guides: guides, lessons: lessons, advanced: advanced };
  }

  function serviceLessons(a, pick, ram, card, liteMachine) {
    var lessons = [];
    function lesson(title, paragraphs, steps, links) {
      lessons.push({
        title: title,
        paragraphs: (paragraphs || []).filter(Boolean),
        steps: steps || [],
        links: links || []
      });
    }
    var tinyCard = card > 0 && card <= 2;
    var modelLine = 'Lite picks the chat model from the card. Under 6 GB it picks a very small model. At about 6 GB it picks a 3-billion model. At about 8 GB it picks a 7-billion model. At about 16 GB it picks a 14-billion model. You can skip the model during install, but then you add one later.';
    if (a.side === 'mac') {
      modelLine = ram >= 16
        ? 'On this Mac, a small chat model can share the unified memory. Close big apps first. Lite will not install that model for you.'
        : 'This Mac is tight for a local model. 16 GB of unified memory is the calm starting size. Lite will not install Ollama on macOS.';
    } else if (tinyCard) {
      modelLine = 'A 1 or 2 GB card cannot hold a useful chat model. Lite can still install, and it will pick a very small model that runs mostly on the processor. It will be slow. A daily chat model wants about 6 GB of card memory or more.';
    } else if (card >= 4 && card < 6) {
      modelLine = 'A 3 or 4 GB card is still small for a 7-billion model. Lite can install a very small model. Treat it as practice until the card is about 6 GB or bigger.';
    }

    var liteHere = liteMachine
      ? 'On this computer, OtaconsKeep Lite is the installer that does Ollama and Piper for you.'
      : (pick === 'proxmox' || pick === 'maclab'
        ? 'On this build, do not put Lite on the Proxmox host. Put Lite on the Windows computer you sit at, or inside one Ubuntu guest.'
        : (pick === 'omarchy' || pick === 'bazzite' || pick === 'alpine' || a.side === 'mac'
          ? 'Lite’s installer is Windows, and Ubuntu or Debian. It is the wrong installer for this system. Use the service lessons below on this computer, and use Lite only on a Windows or Ubuntu machine.'
          : 'Lite’s tested Linux path is Ubuntu or Debian. On Mint, follow the Ubuntu steps only while they match what you see. If a step does not match, stop and use the Ollama download instead.'));

    lesson('OtaconsKeep Lite', [
      'Lite is the free Keep. It gives you agents, memory, a local chat model through Ollama, and Piper so those agents can speak. It runs on your hardware. It does not need a license key.',
      liteHere,
      'Done looks like this: the installer says OTACON IS READY, and a browser on that same computer opens localhost:5757. That address is local. Another computer in the house does not open it unless you set that up later.',
      'Lite needs about 10 GB free for a first install, plus room for the model. The first run can take a while. Leave the window open.'
    ], liteMachine && (pick === 'win' || pick === 'winpro') ? [
      'Sign in to Windows and finish updates.',
      'Open the Lite page and download OtaconsKeep Setup. Watch the install video once if you want a walk-through beside you.',
      'Double-click Setup. If Windows says it protected your PC, choose More info, then Run anyway. That warning is normal for this file.',
      'Say yes when Windows asks permission. Setup may restart the PC once so it can turn on WSL. WSL is a small Linux that Windows uses for the Keep. After the restart, open the same Setup file again if it does not return by itself.',
      'Wait until the window says OTACON IS READY. Then open localhost:5757 on that PC and bookmark it.'
    ] : (liteMachine ? [
      'Install Ubuntu Server and confirm you can sign in from another computer.',
      'Open the Lite page and follow the Ubuntu or Debian steps. Do not invent extra steps.',
      'Wait until it is ready, then open localhost:5757 on that machine.'
    ] : [
      'Get the desk or the server booting first.',
      'Use Lite only on Windows or Ubuntu. The lesson links below are the path for this computer.'
    ]), [
      { name: 'OtaconsKeep Lite', detail: 'The free installer, the Windows download, and the Ubuntu steps.', href: '/otacon/' },
      { name: 'Lite install video', detail: 'Windows, from the download to the ready screen.', href: 'https://youtu.be/OitYjPlbTng' }
    ]);

    lesson('OtaconsKeep Premium', [
      'Premium is a one-dollar seat after Lite already works. It is not a second product and it is not a movie server. Antonio turns the seat on by hand after the donation.',
      'What you get: the five-agent crew, and Video Studio, plus rooms that stay locked on Lite. The Premium page has the Expansion setup. Lite must already open before you run that setup.',
      'What you do not get: Plex, Jellyfin, Sonarr, Radarr, Prowlarr, or Home Assistant. Those are the lessons under this one.',
      tinyCard || card === 4
        ? 'Video Studio wants a real graphics card and Docker, or the portable path the product shows you. A 1 to 4 GB card is the wrong card for that studio. Premium can wait.'
        : 'Video Studio wants a real graphics card. If this computer has about 6 GB or more, it can be the machine that tries it. Read the Premium page before you buy the seat.'
    ], [
      'Prove Lite first. localhost:5757 must open.',
      'Read the Premium page. The seat is the donation plus a license, not a different download of the same installer.',
      'Skip Premium if all you wanted was Ollama, Piper, movies, or the arr apps.'
    ], [
      { name: 'OtaconsKeep Premium', detail: 'The seat, what it includes, and the Expansion setup after Lite.', href: '/premium/' }
    ]);

    lesson('Ollama, the chat model', [
      'Ollama is the program that loads a chat model. The model is the brain. Ollama is the engine that runs it. A parameter is one note the model memorized. More notes need more memory.',
      modelLine,
      liteMachine
        ? 'If you install Lite, do not install Ollama by hand first. Lite installs Ollama and chooses the model. Installing it twice makes a mess.'
        : 'On this system, install Ollama from its own download page. Pick the Windows, Mac, or Linux file that matches the computer in front of you.'
    ], [
      liteMachine ? 'Install Lite and reach OTACON IS READY.' : 'Install Ollama from the download page. Start the app.',
      'Ask one short question. A reply means the model loaded.',
      'Run one model at a time. Close a game or a video export before you chat, if this is the same computer you sit at.',
      card >= 6 && pick === 'proxmox' ? 'On Proxmox, put Ollama in the one guest that owns the graphics card. The other guests do not share that card.' : 'If the reply is very slow, the model is too big for this memory. Use a smaller one. Do not stack a second model on top.'
    ], [
      { name: 'Ollama download', detail: 'The official app, if Lite is not installing it for you.', href: 'https://ollama.com/download' },
      { name: 'OtaconsKeep Lite', detail: 'The path that installs Ollama for you on Windows or Ubuntu.', href: '/otacon/' }
    ]);

    lesson('Piper, the voice', [
      'Piper is the voice. It reads text out loud. There are two different jobs, and they are easy to mix up.',
      'Job one is the Keep. The agents speak with Piper. On Windows and on Ubuntu, Lite installs that voice. Done looks like a spoken preview from the Keep. If chat works and the voice is silent, do not only run Setup again. The Lite page tells you to repair the voice service.',
      'Job two is the house. A microphone hears you, Whisper writes the words, Piper speaks the answer, and Home Assistant connects them. Lite does not build that room for you. Classroom Module 4 does. Follow that module in order. Do not skip ahead to the speaker.',
      pick === 'omarchy' || pick === 'bazzite' || pick === 'alpine' || a.side === 'mac'
        ? 'On this computer, the Keep’s automatic Piper install is the wrong file. Read the Piper project for the engine, and Classroom Module 4 for the house. Put Lite on a Windows or Ubuntu computer when you want the agents to speak.'
        : 'Start with job one if this computer is running Lite. Add job two only after the Keep already says a sentence out loud.'
    ], [
      'Decide which voice you want this week: the Keep’s agents, or a speaker in the room. Do one.',
      'For the Keep, finish Lite until you hear one spoken line.',
      'For the house, open Classroom Module 4 and do the first gate only. Then the next gate. The module is the teacher.',
      'Keep the microphone and the speaker pages inside the house.'
    ], [
      { name: 'Classroom: local voice', detail: 'Whisper hears. Piper speaks. Home Assistant connects them.', href: '/classroom/modules/04-local-voice/' },
      { name: 'Piper project', detail: 'The voice engine, when Lite is not installing it.', href: 'https://github.com/rhasspy/piper' },
      { name: 'OtaconsKeep Lite', detail: 'Agent voice on Windows or Ubuntu, including what to do if chat works and speech does not.', href: '/otacon/' }
    ]);

    lesson('Plex or Jellyfin, the player', [
      'This is the app that plays movies and shows on the TVs and phones in the house. The computer that runs it has to stay on.',
      'Pick one player. Jellyfin is free. Plex is the other famous player and has paid extras. Two players on day one means two libraries to fix.',
      tinyCard
        ? 'A 1 or 2 GB card often cannot convert a video so a phone can play it. Put the original file in the library and let the TV play that file.'
        : 'Play one video you already have before you add anything that fetches more files. If one file will not play, the rest of the stack will not save you.',
      'OtaconsKeep Lite will not install this. Premium will not install it either. The links below are the installers.'
    ], [
      'Make a folder for videos on the big disk, not on the small system disk.',
      'Install Jellyfin or Plex. Point it at that folder.',
      'Copy in one short video you already own. Play it on a TV or a phone in the house.',
      'That play is the done line. Only then go to the arr apps.'
    ], [
      { name: 'Plex install article', detail: 'Official Plex install.', href: 'https://support.plex.tv/articles/200288586-installation/' },
      { name: 'Jellyfin downloads', detail: 'The free player, if you do not want Plex.', href: 'https://jellyfin.org/downloads/' }
    ]);

    lesson('The arr apps: Prowlarr, Sonarr, Radarr', [
      'Arr is the family name. These apps do not play video. They file shows and movies into folders. Plex or Jellyfin plays whatever lands in the folder.',
      'Prowlarr is the address book. It holds the search places once, and shares that list with the other two. You should not type the same list into Sonarr and again into Radarr.',
      'Sonarr is for TV shows. It watches for episodes and puts the files in the show folder. Radarr is the same idea for movies.',
      'Install them in this order: the player, then Prowlarr, then Sonarr, then Radarr. One web page must open from another computer in the house before you install the next app.',
      'TRaSH Guides are the articles that explain quality profiles. A profile is the rule for which file is good enough. Read that before you let an app grab files by itself. A bad rule fills the disk.',
      'Classroom Module 2 is the map. Module 9 is the disks and Docker. Module 10 is Sonarr and Radarr. The Servarr wiki is the install manual for each app. Keep every one of these pages inside the house.'
    ], [
      'Play one video in Plex or Jellyfin first.',
      'Install Prowlarr. Open its page. Leave the search list empty until the page itself is stable.',
      'Install Sonarr. Connect it to the same video folder. Add one show only.',
      'Install Radarr. Add one movie only.',
      'Read a TRaSH quality page before you turn on automatic downloads.',
      pick === 'alpine' ? 'Do not put this stack on Alpine. Alpine is one job. Ubuntu Server is the computer for these apps.' : 'On a game desk, this stack is happier on a second computer that stays on. The desk can still be the computer you sit at.'
    ], [
      { name: 'Classroom: ARR media', detail: 'The map of the whole movie stack.', href: '/classroom/modules/02-arr-media/' },
      { name: 'Classroom: disks and Docker', detail: 'Where the files live, and how the containers should share them.', href: '/classroom/modules/09-arr-data-compose/' },
      { name: 'Classroom: Sonarr and Radarr', detail: 'The hands-on lesson after one video already plays.', href: '/classroom/modules/10-sonarr-radarr/' },
      { name: 'Servarr wiki', detail: 'Install notes for Prowlarr, Sonarr, and Radarr.', href: 'https://wiki.servarr.com/' },
      { name: 'TRaSH Guides', detail: 'Quality profiles, so the apps keep a good file.', href: 'https://trash-guides.info/' }
    ]);

    if (pick === 'omarchy') {
      lesson('Omarchy, this desk', [
        'You picked Omarchy. It is a good daily Linux desk: Arch Linux, already dressed, keyboard first. The windows sit in a grid. You drive them from the keyboard.',
        'It is a poor closet server and a poor place for the only copy of your photos. New anti-cheat games still want Windows or Bazzite.',
        'The Lite installer is not written for Arch. Do not run it here. Ollama comes from Ollama’s download. Piper for the house comes from Classroom Module 4 and the Piper project.'
      ], [
        'Read the install notes on omarchy.org all the way through before you erase a disk.',
        'Keep a second computer nearby for the first week.',
        'After the desk boots, add one app from the lessons above. Ollama is a fair first app. The movie stack can wait, or it can live on another computer.'
      ], [
        { name: 'Omarchy', detail: 'The install notes for this desk.', href: 'https://omarchy.org/' }
      ]);
    } else if (a.side === 'linux' && pick !== 'proxmox' && pick !== 'ubuntu' && pick !== 'alpine') {
      lesson('Omarchy, the other good desk', [
        'Omarchy is still a good choice. It is Arch, set up as a keyboard desk, for someone who can fix an update. Mint is the friendly first desk. Bazzite is the game desk. Omarchy is the sharp daily desk after those feel small.',
        'It is not the computer that should stay in a closet running Plex. And the Lite installer is not for Arch.'
      ], [
        'Stay on the system you just picked until it boots and one app works.',
        'When you want this desk later, install it from omarchy.org onto its own disk. Copy your files off that disk first.'
      ], [
        { name: 'Omarchy', detail: 'A good Linux desk when you can fix an update.', href: 'https://omarchy.org/' }
      ]);
    } else if (pick === 'proxmox' || pick === 'ubuntu' || pick === 'alpine') {
      lesson('Omarchy stays a desk', [
        'Omarchy is a good Linux desk, and this computer is the house server. Do not replace the server with Omarchy. If you want that keyboard desk, it belongs on a second computer you sit at.'
      ], [], [
        { name: 'Omarchy', detail: 'For a desk computer, not for this server.', href: 'https://omarchy.org/' }
      ]);
    } else {
      lesson('Omarchy, if you add a Linux desk', [
        'Omarchy is a good Linux desk. It is Arch, already set up, keyboard first. Pick it when you can fix an update. Mint is the friendly first Linux. Bazzite is the game desk. Omarchy is the sharp daily desk after those feel small.',
        'It is not the next click on this computer. It belongs on its own machine. The Lite installer is not written for it.'
      ], [], [
        { name: 'Omarchy', detail: 'The install notes, for a later Linux desk.', href: 'https://omarchy.org/' }
      ]);
    }

    if (pick === 'bazzite') {
      lesson('Bazzite, this game desk', [
        'Bazzite is the Linux system you sit at to play. Steam is the first app. The NVIDIA download is only for an NVIDIA card. AMD and Intel use the other image.',
        'House apps such as Plex and the arr stack are calmer on a second computer. This one stays the game desk. Lite’s installer is not for Bazzite.'
      ], [
        'Install Bazzite from the docs. Copy files off the disk first.',
        'Open Steam and sign in. Play one game before you add Ollama or a movie server.'
      ], [
        { name: 'Bazzite docs', detail: 'The install notes, including which image matches the graphics card.', href: 'https://docs.bazzite.gg/' }
      ]);
    }

    if (hasJob(a, 'smart') || pick === 'proxmox' || pick === 'ubuntu') {
      lesson('Home Assistant', [
        'Home Assistant is the app for lights, sensors, and switches. It has its own web page. That page stays inside the house.',
        pick === 'proxmox'
          ? 'On Proxmox, give it a guest of its own with 4 GB of memory. Do not pile it onto the host.'
          : 'Install it after the computer is calm. One new app, prove the page opens, then stop for a week.'
      ], [
        'Open the official install page and pick the path that matches this computer.',
        'Then use Classroom Module 3 before you connect anything you care about.',
        'Do not forward the Home Assistant page to the internet.'
      ], [
        { name: 'Home Assistant install', detail: 'The official install guide.', href: 'https://www.home-assistant.io/installation/' },
        { name: 'Classroom: Home Assistant', detail: 'The house lesson, before remote access.', href: '/classroom/modules/03-home-assistant/' }
      ]);
    }

    return lessons;
  }

  function advancedLayer(a, pick, ram, card) {
    var out = [];
    function lesson(title, paragraphs, steps, links) {
      out.push({ title: title, paragraphs: paragraphs, steps: steps || [], links: links || [] });
    }
    var linuxDesk = a.side === 'linux' && (pick === 'bazzite' || pick === 'mint' || pick === 'omarchy' || pick === 'maclab');
    lesson('Proton, and what actually breaks Linux games', [
      'Proton is Valve’s compatibility layer. It is Wine, plus DXVK and VKD3D, which turn DirectX calls into Vulkan so a Windows game can draw on Linux. Steam installs Proton. A native Linux build of a game does not need it.',
      'Use Valve’s Proton first: a numbered Proton, Proton Experimental, or Proton Hotfix. Proton-GE is a community build from GloriousEggroll. It can fix a game Valve’s build has not patched yet. It is not Valve support, and it is not required for every game.',
      'Easy Anti-Cheat and BattlEye have a Proton mode, and it is opt-in per game. The studio has to turn that mode on. If they do not, the game tries to load a Windows kernel driver, Proton cannot load that driver, and the game refuses to start. Support can also be removed later. In September 2026 Ubisoft turned off the Linux Easy Anti-Cheat runtime for For Honor, and the game stopped launching on Steam Deck and on desktop Linux.',
      'Kernel anti-cheat is a harder wall. Systems such as Riot Vanguard and Ricochet expect a Windows kernel driver. Proton does not emulate that. There is no driver setting that fixes it. Those games stay on Windows.',
      'Some games allow a Steam Deck and block other desktop Linux. Steam Deck Verified is a useful hint, not a promise for your Mint or Bazzite PC. Check ProtonDB for crowd reports, and AreWeAntiCheatYet for the anti-cheat column. A report from last year can be wrong this month.',
      'In the Steam tools list, install Proton EasyAntiCheat Runtime and Proton BattlEye Runtime. Without those, a game that did opt in can still fail the handshake.',
      linuxDesk
        ? 'This build is a Linux desk, so Proton is part of the plan if you play Windows games. New anti-cheat games that did not opt in still want a Windows computer beside this one.'
        : 'If this computer is Windows, you do not need Proton here. Proton matters when the game machine is Linux or a Steam Deck. Keep Windows for the games whose anti-cheat has no Linux runtime.'
    ], [
      'Install Steam. In Steam, open the tools list and install both Proton runtimes named above.',
      'Try the game on Valve’s Proton before you add a community Proton.',
      'Look the game up on ProtonDB and on AreWeAntiCheatYet before you blame the graphics card.',
      'The first launch can stutter while shaders compile. That cache is normal. A second launch should be calmer.',
      'If the game is black or crashes, change the Proton version for that game, then reboot once. Reinstalling the whole system is not the first fix.',
      'A 1 or 2 GB card does not become a new-game card because Proton is installed. Proton does not add memory.'
    ], [
      { name: 'Valve Proton', detail: 'The compatibility project Steam uses.', href: 'https://github.com/ValveSoftware/Proton' },
      { name: 'ProtonDB', detail: 'Crowd reports for one game at a time. Read the date.', href: 'https://www.protondb.com/' },
      { name: 'AreWeAntiCheatYet', detail: 'Which anti-cheat a game uses, and whether Linux is in or out.', href: 'https://areweanticheatyet.com/' },
      { name: 'GamingOnLinux anti-cheat check', detail: 'How to read Steam Deck status versus desktop Linux.', href: 'https://www.gamingonlinux.com/guides/view/anticheat-check-which-competitive-games-actually-work-on-linux-steamos/' }
    ]);

    lesson('Linux graphics drivers, and the failures that look like a dead game', [
      'NVIDIA and AMD are different installs. Mixing them up is how a desk ends up with a black screen.',
      'NVIDIA games want the current proprietary driver. Nouveau, the open basic driver, will show a desktop and will not carry new games. On Bazzite, download the NVIDIA image only when the card is NVIDIA. On Mint or Ubuntu, install the driver from the distro’s driver tool, not from a random .run file off a forum.',
      'After a kernel update, a DKMS NVIDIA module has to rebuild. If it does not, the next boot has no NVIDIA driver. An image-based system such as Bazzite ships the driver inside the image, so you update the image instead of compiling a module by hand. Secure Boot can refuse an unsigned module. Either enroll the key the distro shows you, or turn Secure Boot off while you learn. Do not disable it and then forget why the disk is less protected.',
      'AMD’s normal path is the amdgpu driver in the kernel plus Mesa in userspace. You usually do not install a separate AMD “game driver” the way NVIDIA’s panel works. A brand-new AMD card can need a newer kernel than an old Ubuntu LTS has. If the card is missing, check the kernel version before you conclude the card is dead.',
      'Wayland is the modern display server. A few games, capture tools, and overlays still misbehave on it. A Proton version change is the smaller experiment. Switching the whole desk back to X11 is the later one.',
      'One card, one heavy job. A game and a local model at the same time fight over the same memory. Close one before you start the other.'
    ], [
      'Confirm the card in a terminal the distro documents: NVIDIA’s nvidia-smi, or AMD’s listing in the kernel log. If the tool is missing, the driver is missing.',
      'On Bazzite, match the image to the card. NVIDIA image for NVIDIA. The other image for AMD or Intel.',
      'On Mint or Ubuntu, install the packaged driver and reboot once. Do not stack a second driver on top.',
      'After the next kernel update, reboot and check the same tool again before you launch a game.',
      'If only one game fails anti-cheat, stop changing drivers. That failure is the studio’s runtime, not the card.'
    ], [
      { name: 'Bazzite docs', detail: 'Which image matches NVIDIA, AMD, and Intel.', href: 'https://docs.bazzite.gg/' },
      { name: 'Valve Proton', detail: 'Driver problems and Proton problems are different bugs.', href: 'https://github.com/ValveSoftware/Proton' }
    ]);

    lesson('LAN, WAN, VLANs, and the firewall', [
      'The LAN is the house network. The WAN is the internet side of the gateway. Your laptop should live on a private address, the ranges 10.x, 172.16 through 172.31, or 192.168.x. The address your internet provider gives the gateway is the WAN address. Do not put a server on the WAN address by forwarding every port.',
      'A VLAN is an 802.1Q tag, a number on the Ethernet frame. One cable can carry several networks because each frame says which network it belongs to. An access port is untagged: a PC, a camera, or a console gets one network and never sees the tag. A trunk is tagged: the link to a server, a hypervisor, or another switch carries many VLANs, and both ends must agree on the numbers.',
      'Creating a VLAN does not isolate it. On a UniFi gateway the default is often that VLANs can still route to each other until you write firewall rules. Isolation is the rule, not the checkbox that created the network. A guest network is the pattern that starts closer to “internet only.”',
      'The UniFi Dream Machine Pro is a gateway, not a magic switch. Ubiquiti’s tech specs list a stateful firewall, application filtering, VLAN segmentation, intrusion detection and prevention, multi-WAN load balancing, and LACP. Read the current tech-spec page for the ports on the unit you buy. The Pro is the edge. Cameras and access points still need a switch that can feed them power.',
      'A stateful firewall remembers a connection you started, so the reply is allowed home. A new connection from the internet is dropped unless you forwarded it. Do not forward the Proxmox page, the ESXi page, the NAS admin page, Remote Desktop, or the arr apps. If you need to reach home from outside, use a VPN into the house, then reach the admin page from inside.',
      'A practical split is four networks: people you trust, servers, cameras and smart devices, and guests. Guests get the internet and nothing else. Cameras do not get a path to your laptop except the one viewer you allow. Servers can see the disk share. They do not need to see the camera web page.'
    ], [
      'Draw the four networks on paper before you click. Write the VLAN number and the subnet next to each name.',
      'On the UDM Pro, create the networks in the UniFi Network app. There is no EdgeRouter-style command line on UniFi OS.',
      'Set each wall port to one untagged network. Set the port that feeds the server to a trunk of only the VLANs that server should carry.',
      'Add firewall rules that deny the paths you do not want, then test from a laptop: a guest phone should not open the NAS.',
      'Leave IDS on only after the network already passes traffic. A threat filter that is too heavy can slow the gateway. Read the spec for the throughput with IDS on, and do not guess it.'
    ], [
      { name: 'UDM Pro tech specs', detail: 'Firewall, VLAN, multi-WAN, and LACP as Ubiquiti lists them today.', href: 'https://techspecs.ui.com/unifi/cloud-gateways/udm-pro' },
      { name: 'Western Digital CMR and SMR note', detail: 'Not a network page. Use it when you buy the disks in the next lesson.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/29458' }
    ]);

    lesson('Switches: Layer 2, Layer 3, PoE, and smart ports', [
      'A Layer 2 switch forwards frames by MAC address. It can separate VLANs. It does not, by itself, route between those VLANs. Routing is a Layer 3 job. Your UDM Pro can do that routing. A Layer 3 switch can also route, in hardware, so two servers on different VLANs do not have to hairpin through the gateway. A small house does not need a Layer 3 switch. A lab with fast storage and many VLANs might.',
      'An unmanaged switch has no VLAN screen. If you plug a trunk into it, tags get stripped or leaked and two networks become one. Any link that carries more than one VLAN needs a managed switch, sometimes sold as a smart switch. On that switch you mark access ports and trunk ports. The names must match the gateway.',
      'PoE means the switch feeds power down the same cable as the data. The standards, at the switch port, are about 15.4 watts for 802.3af, about 30 watts for 802.3at (PoE+), and about 60 or 90 watts for 802.3bt (PoE++). The device receives less after the cable. A phone is often af. A Wi-Fi 6 access point or a moving camera may want at or bt. Add the watts of every device. The switch’s total budget is smaller than “maximum per port times every port.”',
      'Buy the PoE class you measured. A non-PoE switch plus a pile of injectors works, and it is messier. Do not power a camera from a port that cannot supply its class.'
    ], [
      'List every powered device and its PoE class before you pick the switch.',
      'Use a managed switch on every trunk. Leave unmanaged switches for single-network rooms only.',
      'Label the ports: access VLAN number, or trunk. Future you will not remember.',
      'If the gateway already routes between VLANs, do not also turn on routing on the switch unless you have drawn which device owns the gateway address. Two routers on one VLAN fight.'
    ], [
      { name: 'UDM Pro tech specs', detail: 'What the gateway does, separate from what the switch must do.', href: 'https://techspecs.ui.com/unifi/cloud-gateways/udm-pro' }
    ]);

    lesson('Load balancing, including the ESXi screen people misread', [
      'Three different features share this name. They do not replace each other.',
      'First, multi-WAN load balancing on a gateway such as the UDM Pro. That spreads the house across two internet lines. It does not make one VM faster, and it does not split one download across both lines in a magical way. A single connection still picks one path.',
      'Second, an application load balancer. That is a program such as HAProxy in its own virtual machine. It has an address, and it forwards web requests to two or more app servers. You build this only when you already have two healthy copies of the same app. It is not a checkbox on the hypervisor.',
      'Third, NIC teaming on ESXi, which VMware’s screen calls load balancing. A standard vSwitch can spread virtual machines across physical cables. The default, route based on the originating virtual port, is the safe one: each VM sticks to one uplink, and the switch does not need a special channel. Route based on IP hash is the one that needs a matching static EtherChannel on the physical switch, with every uplink active. Broadcom’s note on KB 2006129: the hash is the source and destination IP. One pair of addresses stays on one uplink, so one copy to one server does not use both cables. A VM talking to several servers can land on more than one uplink. If the switch is not channeled, IP hash drops traffic. Beacon probing is not supported with IP hash. Only link status counts.',
      'Dynamic LACP is not that standard-switch screen. Broadcom’s vSphere docs put LACP on a vSphere Distributed Switch, in a link aggregation group, with the physical switch set to LACP active. A distributed switch is not included with every ESXi license. If you turn LACP on at the switch and the host is not in the same mode, the link looks plugged in and passes the wrong traffic or none. Beacon probing is not the failure detector you use with LACP.',
      'ESXi VLAN ID 4095 means “pass every tag into the guest.” Use it only when that guest is itself a firewall or a router. A normal VM should get one VLAN number that matches the access network you intended.',
      pick === 'proxmox'
        ? 'This build is Proxmox, not ESXi. The same rule still holds. A Linux bond in LACP mode (802.3ad) works only when the switch side is also LACP. Active-backup is the calm choice until the switch is configured. Do not mix the modes.'
        : 'If you are on Proxmox instead of ESXi, use a Linux bond. Active-backup is the calm mode. LACP (802.3ad) only after the switch is in LACP too.'
    ], [
      'Decide which of the three you mean before you change a port.',
      'Leave ESXi on “route based on originating virtual port” until you have drawn the port channel.',
      'If you choose IP hash, configure the static EtherChannel on the switch first, then the vSwitch, with all those uplinks active. Test from a second computer before you walk away.',
      'Do not enable LACP on only one side.',
      'An application load balancer comes last, after two real copies of the app already answer.'
    ], [
      { name: 'Broadcom: dynamic LACP', detail: 'The distributed-switch LAG, not the standard vSwitch checkbox.', href: 'https://techdocs.broadcom.com/us/en/vmware-cis/vsan/vsan/7-0/vsan-network-design-7-0/advanced-nic-teaming/nic-teaming-configuration-examples/configuration-3-dynamic-lacp.html' },
      { name: 'VMware KB 2006129', detail: 'What IP-hash load balancing actually requires on the switch.', href: 'https://knowledge.broadcom.com/external/article?legacyId=2006129' }
    ]);

    lesson('NAS disks: the colors, CMR, SSD, and M.2', [
      'A NAS is a computer whose job is the disks. TrueNAS, Unraid, or a Ubuntu server can be that computer. The color of a Western Digital sticker is a product line, not a promise. Read the datasheet for the exact model. Lines change.',
      'WD Blue is an everyday desktop disk. WD Black is a performance desktop disk. Neither is the pick for a RAID or ZFS box. WD Purple, and Seagate SkyHawk, are for cameras: a stream of writes, few reads. They are the wrong disk for Plex libraries and for ZFS. WD Gold is an enterprise disk, CMR, for harder duty. Seagate IronWolf and IronWolf Pro are the NAS lines. Seagate Exos is the enterprise line. A Barracuda has shipped as SMR in some sizes. Do not assume.',
      'CMR writes tracks beside each other. SMR overlaps them like roof shingles, so a rewrite can stall while the drive rewrites a whole band. WD’s own note says many plain WD Red drives in the 2 TB to 6 TB sizes used SMR, and that ZFS resilver, the rebuild, does not give an SMR drive the idle time it wants. WD Red Plus and WD Red Pro are the CMR NAS drives they point at for that work. “Red” on the shelf is not enough. Read the label.',
      'A mirror or RAIDZ survives one disk dying. It does not survive fire, theft, or a delete. A backup is a second copy somewhere else.',
      'A hard drive is bad at random small files. Virtual machines, the Keep, databases, and a game library that stutters belong on an SSD. Hard-drive cons: the head has to seek, many spinning disks vibrate each other, a huge drive takes a long time to rebuild, and SMR makes that rebuild worse. NAS-rated drives are built for that vibration. A loose desktop drive in a four-bay box is a gamble.',
      'An SSD has no seek, so it is the right place for the operating system and for apps. Flash wears out. The datasheet’s TBW number is the endurance. A disk that is rewritten all day needs a higher endurance part, not the cheapest QLC stick.',
      'M.2 is a shape, the gumstick connector. It is not a speed. An M.2 drive can be SATA, which is the same speed class as a 2.5 inch SATA SSD, or NVMe, which talks PCIe and is the fast one. A motherboard slot might accept only one of those. Read the slot. “M.2” on the box is not the answer.'
    ], [
      'Put the operating system on an SSD or NVMe. Put movies and photos on CMR hard drives.',
      'Before you buy, open the model’s datasheet and find CMR or SMR. Skip the disk if the sheet will not say.',
      'For ZFS or a RAID rebuild, buy the CMR NAS line: Red Plus, Red Pro, IronWolf, or the enterprise CMR disks. Not Purple. Not a mystery Red.',
      'Match the bay. A 3.5 inch NAS disk does not fit an M.2 slot, and an M.2 does not replace a pile of movie disks.',
      'Keep a second copy of anything you would cry about. The RAID light is not that copy.'
    ], [
      { name: 'WD Red: SMR and CMR', detail: 'Western Digital’s own split of Red, Red Plus, and Red Pro.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/29458' },
      { name: 'How to check CMR or SMR', detail: 'WD’s steps, including where the datasheet says it.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/50697' },
      { name: 'WD color lines', detail: 'The current marketing page. The datasheet still wins.', href: 'https://www.westerndigital.com/solutions/color-drives' }
    ]);

    lesson('A Plex layout, and what the GPU is actually for', [
      'Ideal Plex is boring. The player app and its database sit on an SSD. The video files sit on CMR disks in the NAS. The TV plays the original file when it can. That is direct play. Transcoding is the expensive path: the server converts the file because the phone or the TV cannot play it.',
      'Hardware transcode uses a video encoder, which is not the same circuit as the chip that runs an AI model. NVIDIA calls theirs NVENC. Intel calls theirs Quick Sync. AMD calls theirs VCN. A card can be large for games and still a poor encoder, or small and still able to transcode. A 1 or 2 GB card often cannot convert video for a phone. Prefer direct play, or let the TV do the work.',
      'Do not put the only Plex database on a hard drive that is also rebuilding a RAID. The database wants the SSD. The movies want the CMR pile. One disk dying should not take the only copy of the family videos. RAID is not the off-site copy.',
      'The arr apps file new videos into that same folder. They do not play them. Get one file playing before you turn automatic grabs on. The simple lessons above still own that order.'
    ], [
      'SSD for the system and the Plex data. CMR NAS disks for the library.',
      'Play one file on a TV with transcode forced off. If it plays, you are in the good path.',
      'Turn a hardware encoder on only for the clients that cannot direct-play.',
      'Keep Plex’s admin page on the server VLAN. Do not forward it to the internet. Use the Plex account features or a VPN, and read Plex’s own install article before you open a port.'
    ], [
      { name: 'Plex install article', detail: 'The official install, including where the server should live.', href: 'https://support.plex.tv/articles/200288586-installation/' },
      { name: 'Jellyfin downloads', detail: 'The free player if you skip Plex.', href: 'https://jellyfin.org/downloads/' }
    ]);

    var gpuWork = card >= 24
      ? 'About 24 GB of card memory is the class for a 32-billion-parameter chat model in a 4-bit copy, for picture models, and for short AI video experiments. A 70-billion model still wants more, or it borrows system RAM and gets slow. It is not a movie studio.'
      : (card >= 16
        ? 'About 16 GB fits 14-billion chat models more comfortably. A 32-billion model is tight. A 70-billion model does not belong here. Picture models fit better than on an 8 GB card. AI video is still a short experiment, not a pipeline.'
        : (card >= 12
          ? 'About 12 GB is where a 14-billion-parameter chat model in a 4-bit copy can fit, and where 4K editing starts to be reasonable. Short AI video can start, slowly. Do not game and run the model together.'
          : (card >= 8
            ? 'About 8 GB fits a 7 to 8 billion parameter chat model in a 4-bit copy. Older picture models fit. The larger SDXL picture model is tight. AI video does not fit well.'
            : (card >= 6
              ? 'About 6 GB fits a 7-billion chat model in a 4-bit copy, and a small Whisper hearing model. A 14-billion chat model is too big to feel good. Picture work is light. AI video does not fit.'
              : 'Under about 6 GB, do not plan on a useful chat model on the card. A 1 or 2 GB card can show a desktop and play old games. A 3 or 4 GB card can try a tiny model. The 7-billion class wants more once the conversation memory is counted.'))));
    if (a.side === 'mac') {
      gpuWork = 'This is a Mac. There is no separate NVIDIA card. The unified memory is the pool. At 16 GB a small 7-billion model can run if the Mac is quiet. At 32 GB local chat is a real tool. NVIDIA-style AI video still wants a PC card. CUDA guides do not apply.';
    }
    lesson('GPUs for chat, pictures, and video', [
      'The number that matters for a model is the card’s own memory, the VRAM. The marketing name matters less. A parameter is one note the model memorized. A 4-bit copy stores those notes in less memory and is a little less sharp than a fuller copy.',
      gpuWork,
      'Chat is inference: the model is already trained, and you ask it questions. Picture models such as Stable Diffusion 1.5 are the smaller image job. SDXL is the heavier image job. AI video is heavier than both and wants the 12 GB class before it is even a slow experiment, and the 24 GB class before it is a fair experiment.',
      'Video editing is a different job from AI video. DaVinci or Resolve on a desk uses the card to draw frames. A NAS does not edit the wedding. The desk edits. The NAS stores.',
      'One heavy job at a time. The encoder that helps Plex, the cores that draw a game, and the memory that holds a model are sharing one card.'
    ], [
      'Write down the card memory in GB before you download a model.',
      'Start with a 7-billion 4-bit chat model only if you have about 6 GB or more, or a quiet 16 GB Mac.',
      'Add a picture model only after chat already answers.',
      'Leave AI video until the card is in the 12 GB class or better, and keep the clips short.',
      'Do not run that model on the Plex box at the same time you transcode a movie, unless the card is the 24 GB class and you have watched the memory.'
    ], [
      { name: 'Ollama download', detail: 'Inference, the chat runtime. Not a training suite.', href: 'https://ollama.com/download' }
    ]);

    lesson('What the model actually computes', [
      'Picture a very serious autocomplete. It does not look up an answer. It reads the tokens so far and scores every token that could come next. A token is a chunk of text, a word or a piece of a word. The score list is the logits: one number per token in the vocabulary. A higher logit means the weights prefer that token right now. The model has not chosen yet.',
      'The softmax turns scores into chances that add up to 1. If z_i is the logit for token i, and T is the temperature, the chance is P(i) = exp(z_i / T) divided by the sum of exp(z_j / T) over every token j. exp is the exponential. At temperature 1 this is the distribution the weights learned. Ollama’s documented default temperature is 0.8, so a normal run is already a little sharper than that raw distribution.',
      'Try a tiny vocabulary after the words “the cat sat on the”: mat with logit 4, hat with logit 2, dog with logit 0. At temperature 1 the chances are about 0.87, 0.12, and 0.02. The model is not “saying mat.” It is holding a weighted coin, and sampling flips it. At temperature 0.5, mat’s chance rises to about 0.98. At temperature 2 the chances flatten to about 0.67, 0.24, and 0.09, so dog shows up more often. Nothing in the weights changed. Only the coin changed.',
      'As T gets very small, the largest logit wins every time. That is greedy decoding. As T grows without a bound, the chances flatten toward 1 divided by the vocabulary size. A high temperature does not add a fact. A token whose logit is far below the others stays rare until the draw is basically noise.',
      'The prompt is the left side of a conditional. The weights define P(next token | tokens so far). Your sentence, the hidden template, the system text, and the earlier turns are “tokens so far.” Change one of those tokens and every logit can change, because the network reads the whole prefix. A prompt does not edit a weight. It chooses which distribution you sample.',
      'Each token you accept is appended, and the next draw is conditional on that longer prefix. A risky early pick changes every later logit. That is why a high temperature drifts: the system text is only the beginning, and a wild token becomes part of the prompt the model reads next. A low temperature keeps walking the high-probability path, so the growing prompt stays near the peak your prefix created, if that peak was actually the one you wanted.',
      'Training looks at a different number. The loss at one position is the cross-entropy L = -log P(correct next token). If the model gave the true token probability 1, the loss is 0. If it gave that token probability 0.1, the loss is about 2.3, because the natural log of 0.1 is about -2.3. The gradient is the slope of that loss for each weight: which way to nudge the weight so the true token’s chance rises. Chat never computes that loss. Chat only samples. The Adam lesson is that nudging. This lesson is the coin.'
    ], [
      'Say the next word of a sentence out loud, then name two other words you might have said. That list, with chances, is what the model computes.',
      'When an answer looks random, ask whether the prompt put the right token on top, or whether the temperature is spending draws on the tail.',
      'When an answer ignores an instruction after a long chat, suspect the window before you suspect the weights. The context lesson is next.'
    ], [
      { name: 'Ollama Modelfile', detail: 'Where temperature and the other sampling numbers are documented.', href: 'https://docs.ollama.com/modelfile' }
    ]);

    lesson('Sampling knobs, and how they meet the prompt', [
      'These numbers do not train the model. They decide how the next token is picked, and they are the PARAMETER lines in an Ollama Modelfile. Ollama’s documented defaults are temperature 0.8, top_k 40, top_p 0.9, min_p 0.0, repeat_penalty 1.0, repeat_last_n 64, num_ctx 2048, and num_predict -1. A num_predict of -1 means it may continue until a stop string. Change one of them when you are testing, or you will not know which knob moved the answer.',
      'Temperature divides every logit by T before the softmax, as in the lesson above. Below 0.8 the coin sticks closer to the favorite token. That helps a command, a JSON blob, or a fact, when the prompt already made the right token the favorite. Above 0.8 the coin spreads. Style and brainstorms move, and so do wrong tokens that only had a small chance. If the prompt made a wrong token the favorite, a lower temperature makes that wrong token more stubborn. Temperature cannot repair a prefix whose peak is wrong.',
      'top_k keeps only the k highest logits and drops the rest, then rescales the survivors so they add to 1. The default is 40. It is a count, not a probability. A token just outside the top 40 is gone even if it was almost as likely as number 40. A k of 10 is a short list. A k of 100 lets more of the tail in.',
      'top_p is nucleus sampling, from Holtzman and colleagues in 2019. Sort tokens from most likely to least. Keep the smallest set whose chances add up to at least p, drop the rest, and rescale. The default is 0.9, so the rare tail that makes up the last 10 percent is cut. A p of 0.5 keeps only the head. A p of 0.95 keeps more tail. Holtzman’s point was that the far tail of a language model is unreliable, and always taking the single most likely token makes text bland and repetitive. top_p and top_k stack: a token has to survive the cuts you turned on. Ollama’s docs say they work together.',
      'min_p is a floor relative to the favorite. A token survives only if its chance is at least min_p times the chance of the most likely token. Ollama’s example: min_p 0.05 and a favorite at 0.9 drops anything under 0.045, because 0.05 times 0.9 is 0.045. The default is 0.0, so this cut is off. min_p gets stricter when the model is confident, because the favorite’s chance is high, and looser when the model is unsure. top_p always tries to cover a fixed fraction of the probability. They are different knives.',
      'repeat_penalty looks back repeat_last_n tokens, 64 by default, and pushes logits of tokens that already appeared. The default penalty is 1.0, which Ollama documents as off. 1.1 is a light nudge. 1.5 is harsh and can force odd synonyms. A value under 1, their example 0.9, is more lenient and can encourage repeats. The usual rule is: if the penalty is above 1, a positive logit of a recent token is divided by the penalty, and a negative logit is multiplied by it, so either way that token gets less likely. This edits logits for the draw. It does not edit the saved weights, and it does not rewrite your system text. It exists because a low temperature loves the peak, and the peak of “continue” is sometimes the same phrase again.',
      'num_ctx is how many tokens of prefix fit. The default is 2048, which is small once a system message, a few examples, and a long chat are all in the prefix. Tokens that fall off the front are no longer in the conditional, so the distribution forgets them. Templates usually put the system message first, so a full window drops the instructions and the model seems to stop following rules that are still in your file. Raising num_ctx keeps more of the prompt and uses more memory. It does not make the weights smarter. num_predict caps how many new tokens may be appended. stop halts when a string appears, usually a template end marker. A wrong stop cuts a good answer. A missing stop lets the model start writing the next user turn.',
      'seed fixes the random draws. Ollama’s example is seed 42: the same prompt and the same parameters replay the same text. Hold the seed still while you compare two temperatures, or you cannot tell the prompt from the coin. Change the prompt and the same seed is still a new answer, because the logits changed.',
      'Put the pieces in one line. The prompt, through the weights, builds the logits z. Temperature rescales z. top_k, top_p, and min_p delete coordinates and rescale. repeat_penalty nudges coordinates that match recent tokens. The words you read are one sample from whatever is left, and that sample is written back into the prompt before the next sample. A strict system message shifts z only as far as the weights know that behavior. A high temperature then spends draws on the leftover tail, those tokens join the prefix, and the persona leaks. A very low temperature shows you the single peak more reliably. If the system message never moved that peak, the low temperature repeats the generic peak and it feels like the prompt did nothing. Fix the prompt when the peak is wrong. Fix the temperature when the peak is right and the samples wander.'
    ], [
      'Write down temperature, top_p, and num_ctx before you change a model. Ollama’s defaults are 0.8, 0.9, and 2048.',
      'Ask one question with seed 42. Change only temperature. Ask again. The difference is the coin.',
      'If a long chat forgets the instruction, raise num_ctx before you rewrite the instruction. If the instruction is forgotten on the first reply, the peak is the prompt, not the window.',
      'Do not turn temperature down and top_p down and repeat_penalty up in the same test. You will not know which one you felt.'
    ], [
      { name: 'Ollama Modelfile', detail: 'The defaults for temperature, top_k, top_p, min_p, repeat, num_ctx, and seed.', href: 'https://docs.ollama.com/modelfile' },
      { name: 'Nucleus sampling, Holtzman and others, 2019', detail: 'Why cutting the tail (top_p) is different from always taking the favorite token.', href: 'https://arxiv.org/abs/1904.09751' }
    ]);

    lesson('Build or change an Ollama model without training', [
      'Ollama runs a model. Writing a prompt does not train one. A custom model here is a Modelfile: a base, plus text, plus the sampling defaults from the lesson above. The official page is the Modelfile reference. Read it again if a flag on this page and that page ever disagree. Their page wins.',
      'FROM names the base. FROM llama3.2 uses a library model you pulled, and you pick a size that fits the card in the GPU lesson. FROM ./file.gguf imports a GGUF file, which is a quantized copy of weights someone already built. FROM a directory can import Safetensors when the architecture is one Ollama supports. Importing copies weights onto the machine. It does not run Adam, and it does not make the model know your files.',
      'SYSTEM is the system message. TEMPLATE is the Go template that decides where that message sits among special markers. The template variables are .System, .Prompt, and .Response. The model never sees the word SYSTEM. It sees the tokens the template emits. Those markers were in the training data for that base. If you invent a different template, the system sentence lands where the weights do not treat it as an instruction, the logits barely move, and people blame temperature. Keep the template that ollama show --modelfile prints for that base.',
      'MESSAGE user and MESSAGE assistant append an example conversation. That is few-shot prompting. Those turns become more prefix, so they change P(next token | prefix). Use them to show a shape: a one-line answer, a yes then a no, a JSON object. They are not a fine-tune. A handful of examples steers the next draw. They do not rewrite the weights. A long pile of MESSAGE lines also spends the num_ctx budget, and the oldest lines, often the system message, fall off first.',
      'PARAMETER lines become the defaults for this named model. A chat app can still override them for one request. The file is the default coin, not a lock. Quantization is not one of those lines. Q4 or Q8 is a property of the weight file you pulled or imported. A 4-bit file is a smaller, slightly less exact copy of the same trained model. Temperature does not quantize, and a quantize tag does not set temperature.',
      'What the system text can do is shift logits toward continuations that were likely, in training, after that kind of instruction. “Answer in one sentence” works when the base learned to follow that shape. “Know my private notes” does nothing unless those notes are in the prefix. The system message is not a database. If the user message contradicts the system message, both are in the prefix, and the weights decide which peak wins. Low temperature shows that winner more often. It does not invent a compromise the weights never scored.',
      'Build it in four moves. Pull a base you have the right to use, or point FROM at a GGUF you have the right to use. Save a Modelfile. Run ollama create your-name -f Modelfile. Run ollama run your-name. Read the result back with ollama show --modelfile your-name. To change the system text or a knob, edit the file and create again. Create again rebuilds the blueprint. It does not resume training.'
    ], [
      'Pull a base that fits the card memory from the GPU lesson.',
      'Write FROM for that base. Copy the template from ollama show --modelfile. Do not invent the marker tokens.',
      'Set SYSTEM in a few sentences. Set temperature and num_ctx on purpose. 2048 is the default window.',
      'ollama create your-name -f Modelfile, then ask one question with seed 42.',
      'Change only SYSTEM, create again, same seed, same question. The difference is the prefix moving the distribution.',
      'Change only temperature, same system text, same seed. The difference is the coin, and the way each sampled token rewrites the prefix for the next token.'
    ], [
      { name: 'Ollama Modelfile', detail: 'FROM, PARAMETER, TEMPLATE, SYSTEM, and MESSAGE.', href: 'https://docs.ollama.com/modelfile' },
      { name: 'Ollama library', detail: 'Bases you can pull. Match the size to the card.', href: 'https://ollama.com/library' },
      { name: 'Ollama download', detail: 'The app that runs create and run.', href: 'https://ollama.com/download' }
    ]);

    lesson('Adam, and the knobs people confuse with it', [
      'Adam is a training optimizer from Kingma and Ba, 2014, “Adam: A Method for Stochastic Optimization.” It is how a model learns. It is not a setting inside Ollama, and turning it does not make a downloaded chat model smarter.',
      'Training looks at the gradient, the direction that reduces the error. Adam keeps two running averages for every parameter. The first moment is a moving average of the gradient, the mean. The second moment is a moving average of the squared gradient, the uncentered variance. The step is the first, bias-corrected, divided by the square root of the second.',
      'Those averages start at zero, so the early steps are biased toward zero. Bias correction divides that startup error out. The paper shows that skipping the correction hurts most when the second-moment decay is aggressive, because the early steps get huge. RMSProp is the close cousin without that correction. AdaGrad is the older method that keeps a growing sum of squared gradients and can stall. AdamW, from Loshchilov and Hutter, moves weight decay outside the adaptive step so the decay is not shrunk by the second moment. Modern language-model fine-tunes usually say AdamW, not the 2014 Adam alone.',
      'The defaults people cite from the published method are a learning rate of 0.001, beta1 of 0.9, beta2 of 0.999, and epsilon of 1e-8. An early preprint writes the decays in a confusing way. Do not type numbers from a random screenshot. If you train, use the defaults your training tool documents, then change one number.',
      'One step, in the symbols. g_t is the gradient at step t, the slope from the cross-entropy in the earlier lesson. m and v start at 0. m_t = beta1 times m at the previous step, plus (1 - beta1) times g_t. v_t = beta2 times v at the previous step, plus (1 - beta2) times g_t squared. With beta1 at 0.9, m is a short memory, about 1 / (1 - 0.9) = 10 steps. With beta2 at 0.999, v is a long memory, about 1 / (1 - 0.999) = 1000 steps. A noisy gradient gets smoothed in m. A weight that has been swinging builds a larger v, and the update shrinks, because the step divides by the square root of v. A quiet weight keeps a small v, so a real gradient can still move it.',
      'Those averages start at 0, so the first m is only (1 - beta1) times the gradient: a tenth of g when beta1 is 0.9. Bias correction divides m by (1 - beta1 to the power t), and divides v by (1 - beta2 to the power t). Call the results m-hat and v-hat. The weight update is theta_t = theta at the previous step, minus alpha times m-hat, divided by (the square root of v-hat, plus epsilon). alpha is the learning rate. epsilon, 1e-8, only keeps the division off zero. Skip the correction on v and the first steps can explode: v is still near 0, its square root is tiny, and dividing by it makes a huge jump. That is the failure the Adam paper points out. RMSProp is this shape without the correction. AdaGrad adds the squared gradients into a sum that never forgets, so the steps shrink forever.',
      'The learning rate is the size of the step. Too high and the loss explodes or becomes NaN. Too low and the model barely moves. You watch the loss. You do not guess a heroic rate. The loss should trend down. A loss that blows up is a step that was too large, not a prompt you can fix in Ollama.',
      'AdamW, Loshchilov and Hutter, 2017, adds a separate shrink. After the adaptive step, the weights also move by a small multiple of themselves, and that multiple is not divided by the square root of v. Plain Adam with L2 folds the decay into g, so the decay gets shrunk on the weights that are already moving a lot. The decay and the learning rate then tangle. Decoupling them is why language-model fine-tunes say AdamW. Their paper is about that separation. It is still training. It is still not a Modelfile line.',
      'Inference is the other job, the one Ollama does, and the sampling lessons above are the formulas. Temperature rescales logits. top_p cuts the tail. num_ctx decides how much of the prompt still fits. Quantization, the Q4 or Q8 in a model name, shrinks a trained file so it fits in less memory. Q4 is smaller and a bit less sharp. Q8 is closer to the original weights and heavier. None of those set beta1. None of them are Adam. A PARAMETER line does not change theta. A training step does not rewrite the SYSTEM text. After a real fine-tune the same system text can sit on a different peak, because theta changed. The coin on top of that peak is still temperature.',
      'Full training stores the weights plus Adam’s two moment vectors, so it needs much more memory than chatting. That is why a 6 GB card can answer with a 7-billion 4-bit model and still cannot train that model from scratch. LoRA trains a small adapter beside a frozen model. QLoRA keeps the base model quantized and trains the adapter, which is how a smaller card fine-tunes. It is still training. It wants a real card, a dataset you have the rights to, and a run you can stop. A 1 or 2 GB card is not that card. Training a model from nothing is a datacenter job, not this lab.'
    ], [
      'If you only want answers, stay on inference. Install Ollama or Lite. Do not hunt for an Adam checkbox.',
      'If you fine-tune, name the optimizer the tool uses. Expect AdamW. Keep the tool’s default learning rate until a run finishes.',
      'Change one hyperparameter per run. Write down beta1, beta2, the learning rate, and the loss.',
      'Count memory before you start: weights, plus optimizer state, plus the batch. If it does not fit, use a smaller model or LoRA, or stop.',
      'Do not point a training run at a disk that is also your only copy of family photos.'
    ], [
      { name: 'Adam, Kingma and Ba, 2014', detail: 'The paper. Training only. The update with the two averages and the bias correction.', href: 'https://arxiv.org/abs/1412.6980' },
      { name: 'AdamW, Loshchilov and Hutter, 2017', detail: 'Why weight decay is separated from the adaptive step.', href: 'https://arxiv.org/abs/1711.05101' },
      { name: 'Ollama Modelfile', detail: 'Inference knobs. No beta1, no learning rate.', href: 'https://docs.ollama.com/modelfile' }
    ]);

    return out;
  }

  function macModels(ram) {
    var base = 'On a Mac, local models use the same unified memory as your apps. They do not use CUDA, which is the NVIDIA tool most PC AI guides assume. ';
    if (ram <= 8) return base + 'At 8 GB, skip local models or try only a tiny one with every other app closed.';
    if (ram <= 16) return base + 'At 16 GB, a small 7-billion-parameter chat model can run in a 4-bit copy if the Mac is otherwise quiet.';
    if (ram <= 24) return base + 'At 24 GB, mid-size chat models are fair. Do not export a long video at the same time.';
    if (ram <= 32) return base + 'At 32 GB, local chat is a real tool. Picture models exist. NVIDIA-style AI video still wants a PC card.';
    return base + 'At ' + ram + ' GB, larger chat models fit. This is still not a 24 GB NVIDIA card, and a 70-billion model is not the daily plan.';
  }

  var STEPS = [
    {
      id: 'side',
      title: 'Choose your side',
      hint: 'Start with the family you want. The next screens open only that family. Windows, Linux, and Mac are the three sides.',
      choices: [
        { value: 'win', label: 'Windows', detail: 'The normal PC. Games, stores, and the buttons most people know.' },
        { value: 'linux', label: 'Linux', detail: 'Free systems. A friendly desk, a closet server, or a boss of many little computers.' },
        { value: 'mac', label: 'Mac', detail: 'The Apple desk. Quiet, finished, and a different kind of memory.' }
      ]
    },
    {
      id: 'role',
      titleFor: function (a) {
        if (a.side === 'mac') return 'Where does the Mac live?';
        if (a.side === 'win') return 'Where does this Windows PC live?';
        return 'Where does this Linux computer live?';
      },
      hint: 'One computer. Say if you sit at it, if it hides in a closet, or if it tries to do both.',
      choices: [
        { value: 'everyday', label: 'I sit at it', detail: 'Web, school, files, maybe games.' },
        { value: 'server', label: 'It stays on for the house', detail: 'A closet box or a Mac mini. I use another screen to control it.' },
        { value: 'both', label: 'One computer does both', detail: 'I sit at it, and it also runs the house.' }
      ]
    },
    {
      id: 'job',
      multi: true,
      title: 'What jobs matter most?',
      hint: 'Tap every job you care about. Games can sit next to photos, video, or a house server. Then press continue.',
      choices: [
        { value: 'games', label: 'Games', detail: 'Play on this computer. New games, or a smaller library.' },
        { value: 'photos', label: 'Photos', detail: 'Sort, edit, and keep pictures.' },
        { value: 'video', label: 'Video', detail: 'Edit movies, or try AI video.' },
        { value: 'movies', label: 'Movies and TV', detail: 'A library the house can watch.' },
        { value: 'smart', label: 'Smart home', detail: 'Lights, sensors, and voice in the house.' },
        { value: 'ai', label: 'Local AI', detail: 'Chat models that stay in the house.' },
        { value: 'learn', label: 'Learning', detail: 'I want to learn this side for real.' },
        { value: 'files', label: 'Files and backups', detail: 'A safe place for documents and copies.' }
      ]
    },
    {
      id: 'skill',
      titleFor: function (a) {
        if (a.side === 'win') return 'How hands-on do you want Windows to be?';
        if (a.side === 'mac') return 'How far do you want to take the Mac?';
        return 'How well do you know Linux?';
      },
      hintFor: function (a) {
        if (a.side === 'linux') return 'Linux is the family Mint, Ubuntu, Alpine, and Proxmox belong to.';
        if (a.side === 'mac') return 'You can stay in the normal Mac, or add a lab beside it.';
        return 'Home is the simple layer. Pro adds locks, remote desktop, and a practice virtual computer.';
      },
      choicesFor: function (a) {
        if (a.side === 'win') {
          return [
            { value: 'simple', label: 'Just make it work', detail: 'I want the normal Windows desk.' },
            { value: 'steps', label: 'I can follow careful steps', detail: 'I will turn on a few extra tools if they are worth it.' },
            { value: 'switches', label: 'I like the extra switches', detail: 'Remote desktop, disk locks, and a practice virtual computer sound good.' }
          ];
        }
        if (a.side === 'mac') {
          return [
            { value: 'simple', label: 'Keep the Mac simple', detail: 'Photos, video, and normal Mac life.' },
            { value: 'terminal', label: 'I can use Terminal a little', detail: 'I will install a helper app if the steps are clear.' },
            { value: 'lab', label: 'I want a lab next to the Mac', detail: 'The Mac stays. Another computer can run the house.' }
          ];
        }
        return [
          { value: 'new', label: 'Linux is new to me', detail: 'I have not really used it.' },
          { value: 'some', label: 'I have tried it', detail: 'I can click around. The terminal still feels shaky.' },
          { value: 'ok', label: 'I can fix a problem', detail: 'A bad update would annoy me, not stop me.' }
        ];
      }
    },
    {
      id: 'games',
      when: function (a) { return hasJob(a, 'games'); },
      titleFor: function (a) {
        return a.side === 'mac' ? 'What kind of games on this Mac?' : 'What kind of games on this computer?';
      },
      hint: 'Anti-cheat means the game checks that you are not cheating. Many of those games only trust Windows.',
      choices: [
        { value: 'aaa', label: 'New games', detail: 'Including online games that use anti-cheat.' },
        { value: 'some', label: 'Some games', detail: 'Older games, indie games, or a store library is enough.' }
      ]
    },
    {
      id: 'ram',
      titleFor: function (a) {
        return a.side === 'mac' ? 'How much unified memory does the Mac have?' : 'How much memory (RAM) can it have?';
      },
      hintFor: function (a) {
        if (a.side === 'mac') return 'On a Mac, this number is also the graphics memory. The screen and the AI share it. It is not a separate NVIDIA card.';
        return 'RAM is the desk space while you work. It is not the closet where files live.';
      },
      choicesFor: function (a) {
        if (a.side === 'mac') {
          return [
            { value: 8, label: '8 GB', detail: 'Tight. Browsing and writing. Local AI will feel sticky.' },
            { value: 16, label: '16 GB', detail: 'A calm daily Mac. One small model if the Mac is quiet.' },
            { value: 24, label: '24 GB', detail: 'More air for video and mid-size models.' },
            { value: 32, label: '32 GB', detail: 'A strong Mac for Final Cut and local chat.' },
            { value: 64, label: '64 GB', detail: 'A serious Apple-silicon workstation.' },
            { value: 128, label: '128 GB or more', detail: 'A top Mac. Still not an NVIDIA video card.' }
          ];
        }
        return [
          { value: 8, label: '8 GB', detail: 'One job at a time.' },
          { value: 16, label: '16 GB', detail: 'A normal daily computer, or a starter server.' },
          { value: 32, label: '32 GB', detail: 'The start of a real lab.' },
          { value: 64, label: '64 GB', detail: 'A comfortable lab.' },
          { value: 128, label: '128 GB or more', detail: 'A big lab.' }
        ];
      }
    },
    {
      id: 'gpu',
      when: function (a) { return a.side !== 'mac'; },
      title: 'What graphics card do you have?',
      hint: 'The GPU draws games and can run AI. The GB here is the card’s own memory, not the computer’s RAM. A Mac does not get this question, because its graphics share system memory.',
      choices: [
        { value: 'none', label: 'No extra card', detail: 'Only the graphics built into the processor.' },
        { value: 1, label: '1 GB or less', detail: 'A very old card. It shows the desktop. It is not for new games or AI.' },
        { value: 2, label: 'About 2 GB', detail: 'An old card. Old games at low settings. Not a chat-model card.' },
        { value: 4, label: 'About 3 or 4 GB', detail: 'A common older card. Light 1080p games. Still small for AI.' },
        { value: 6, label: 'About 6 GB', detail: 'A card like a 2060. 1080p games and a small chat model.' },
        { value: 8, label: 'About 8 GB', detail: 'A common recent card.' },
        { value: 12, label: 'About 12 GB', detail: 'Room for bigger models and 4K video.' },
        { value: 16, label: 'About 16 GB', detail: 'Strong for 1440p and mid-size models.' },
        { value: 24, label: '24 GB or more', detail: 'Games, pictures, and short AI video.' }
      ]
    },
    {
      id: 'storage',
      title: 'How much storage will hold your files?',
      hint: 'Count the big disks, not only the small drive the system boots from.',
      choices: [
        { value: 256, label: '256 GB', detail: 'System and apps. Not a photo vault.' },
        { value: 1000, label: '1 TB', detail: 'Games or a starter photo library.' },
        { value: 4000, label: 'About 4 TB', detail: 'A real photo pile or a small movie shelf.' },
        { value: 8000, label: 'About 8 TB', detail: 'Family movies or a big camera archive.' },
        { value: 16000, label: '16 TB or more', detail: 'Media-server size. Plan more than one disk.' }
      ]
    },
    {
      id: 'budget',
      title: 'What can you spend if you had to buy the box?',
      hint: 'If you already own it, say so.',
      choices: [
        { value: 'have', label: 'I already own it', detail: 'I am only picking the system.' },
        { value: 200, label: 'Under $200', detail: 'Used tiny office PC money.' },
        { value: 500, label: '$200 to $500', detail: 'A used server or a mini PC.' },
        { value: 1200, label: '$500 to $1,200', detail: 'A starter lab or a nice daily PC.' },
        { value: 'more', label: 'More than $1,200', detail: 'Enough to think about two computers.' }
      ]
    },
    {
      id: 'flavor',
      title: 'Open the last layer',
      hint: 'These are the real builds inside the side you chose. The other sides stay closed. Tap the one that should be yours.',
      choicesFor: function (a) { return flavorChoices(a); }
    }
  ];

  function stepsFor(answers) {
    var a = answers || {};
    return STEPS.filter(function (step) {
      return !step.when || step.when(a);
    });
  }

  function field(step, answers, name) {
    var fn = step[name + 'For'];
    if (typeof fn === 'function') return fn(answers);
    return step[name];
  }

  var PARTS = {
    cpu: [
      { id: 'r5-5600', name: 'AMD Ryzen 5 5600', maker: 'amd', socket: 'AM4', arch: 'Zen 3', cores: 6, threads: 12, watts: 65, igpu: false, memory: 'DDR4', plain: 'A common older AMD chip. Zen 3 on AM4. It does not make a picture by itself. It uses DDR4.' },
      { id: 'r5-5600g', name: 'AMD Ryzen 5 5600G', maker: 'amd', socket: 'AM4', arch: 'Zen 3', cores: 6, threads: 12, watts: 65, igpu: true, memory: 'DDR4', plain: 'Zen 3 with graphics built in. A desk or a small server can skip the extra card. AMD lists this at 65 W.' },
      { id: 'r7-5700x', name: 'AMD Ryzen 7 5700X', maker: 'amd', socket: 'AM4', arch: 'Zen 3', cores: 8, threads: 16, watts: 65, igpu: false, memory: 'DDR4', plain: 'More Zen 3 cores on AM4. Still no picture of its own. Still DDR4.' },
      { id: 'r5-7600', name: 'AMD Ryzen 5 7600', maker: 'amd', socket: 'AM5', arch: 'Zen 4', cores: 6, threads: 12, watts: 65, igpu: true, memory: 'DDR5', plain: 'Zen 4 on AM5. Six cores, 12 threads, 65 W, DDR5, and graphics built in.' },
      { id: 'r7-7700', name: 'AMD Ryzen 7 7700', maker: 'amd', socket: 'AM5', arch: 'Zen 4', cores: 8, threads: 16, watts: 65, igpu: true, memory: 'DDR5', plain: 'Zen 4, eight cores, still the 65 W part, still DDR5. This is not the hotter X model.' },
      { id: 'r9-7900', name: 'AMD Ryzen 9 7900', maker: 'amd', socket: 'AM5', arch: 'Zen 4', cores: 12, threads: 24, watts: 65, igpu: true, memory: 'DDR5', plain: 'Zen 4, twelve cores, the 65 W chip for a heavy desk or a server. Not the 170 W X model.' },
      { id: 'i3-12100', name: 'Intel Core i3-12100', maker: 'intel', socket: 'LGA1700', arch: 'Alder Lake', cores: 4, threads: 8, watts: 89, igpu: true, memory: 'DDR4 or DDR5', plain: '12th-gen Alder Lake with graphics built in. Intel lists 60 W base and 89 W turbo. This checker uses 89 W.' },
      { id: 'i5-12400', name: 'Intel Core i5-12400', maker: 'intel', socket: 'LGA1700', arch: 'Alder Lake', cores: 6, threads: 12, watts: 117, igpu: true, memory: 'DDR4 or DDR5', plain: '12th-gen Alder Lake with graphics. Intel lists 117 W turbo. This checker uses that.' },
      { id: 'i5-12400f', name: 'Intel Core i5-12400F', maker: 'intel', socket: 'LGA1700', arch: 'Alder Lake', cores: 6, threads: 12, watts: 117, igpu: false, memory: 'DDR4 or DDR5', plain: 'Same Alder Lake chip. The F means no picture built in. Add a graphics card.' },
      { id: 'i5-13400', name: 'Intel Core i5-13400', maker: 'intel', socket: 'LGA1700', arch: 'Raptor Lake', cores: 10, threads: 16, watts: 148, igpu: true, memory: 'DDR4 or DDR5', plain: '13th-gen Raptor Lake with graphics. Intel lists 148 W turbo.' },
      { id: 'i5-13400f', name: 'Intel Core i5-13400F', maker: 'intel', socket: 'LGA1700', arch: 'Raptor Lake', cores: 10, threads: 16, watts: 148, igpu: false, memory: 'DDR4 or DDR5', plain: 'Same Raptor Lake chip, no picture built in. Add a graphics card.' },
      { id: 'i5-14600', name: 'Intel Core i5-14600', maker: 'intel', socket: 'LGA1700', arch: 'Raptor Lake', cores: 14, threads: 20, watts: 154, igpu: true, memory: 'DDR4 or DDR5', plain: '14th-gen Raptor Lake refresh with graphics. Intel lists 154 W turbo. This is not the K model.' }
    ],
    board: [
      { id: 'b550', name: 'AMD B550, DDR4, micro-ATX', maker: 'amd', socket: 'AM4', ram: 'DDR4', form: 'matx', plain: 'For Ryzen 5000. Smaller board. DDR4 only.' },
      { id: 'b550-atx', name: 'AMD B550, DDR4, ATX', maker: 'amd', socket: 'AM4', ram: 'DDR4', form: 'atx', plain: 'Same older AMD socket, more room in a bigger case.' },
      { id: 'b650m', name: 'AMD B650, DDR5, micro-ATX', maker: 'amd', socket: 'AM5', ram: 'DDR5', form: 'matx', plain: 'Current AMD socket in a smaller board. DDR5 only.' },
      { id: 'b650', name: 'AMD B650, DDR5, ATX', maker: 'amd', socket: 'AM5', ram: 'DDR5', form: 'atx', plain: 'Current AMD socket, full size. DDR5 only.' },
      { id: 'b650i', name: 'AMD B650, DDR5, mini-ITX', maker: 'amd', socket: 'AM5', ram: 'DDR5', form: 'itx', plain: 'A tiny current AMD board. Read the case page. Tiny cases choke fat cards.' },
      { id: 'b760-d4', name: 'Intel B760, DDR4, micro-ATX', maker: 'intel', socket: 'LGA1700', ram: 'DDR4', form: 'matx', plain: 'Intel socket, older memory. Useful when you already own DDR4.' },
      { id: 'b760-d4-atx', name: 'Intel B760, DDR4, ATX', maker: 'intel', socket: 'LGA1700', ram: 'DDR4', form: 'atx', plain: 'Same Intel DDR4 idea, full size.' },
      { id: 'b760-d5m', name: 'Intel B760, DDR5, micro-ATX', maker: 'intel', socket: 'LGA1700', ram: 'DDR5', form: 'matx', plain: 'Intel socket, new memory, smaller board.' },
      { id: 'b760-d5', name: 'Intel B760, DDR5, ATX', maker: 'intel', socket: 'LGA1700', ram: 'DDR5', form: 'atx', plain: 'Intel socket, new memory, full size.' },
      { id: 'b760i', name: 'Intel B760, DDR5, mini-ITX', maker: 'intel', socket: 'LGA1700', ram: 'DDR5', form: 'itx', plain: 'A tiny Intel board. DDR5. Check the card length.' }
    ],
    ram: [
      { id: 'd4-16', name: '16 GB DDR4', ram: 'DDR4', plain: 'Light desk. Tight if you keep many apps open.' },
      { id: 'd4-32', name: '32 GB DDR4', ram: 'DDR4', plain: 'A calm amount for an older AMD or Intel board.' },
      { id: 'd4-64', name: '64 GB DDR4', ram: 'DDR4', plain: 'For many virtual computers or a heavy editor.' },
      { id: 'd5-32', name: '32 GB DDR5', ram: 'DDR5', plain: 'A calm amount on a new board.' },
      { id: 'd5-64', name: '64 GB DDR5', ram: 'DDR5', plain: 'Room for bigger local models or more house apps.' },
      { id: 'd5-96', name: '96 GB DDR5', ram: 'DDR5', plain: 'A large kit, often two 48 GB sticks. Confirm the board allows it.' }
    ],
    gpu: [
      { id: 'none', name: 'No extra card', watts: 0, plain: 'Fine only if the processor can make a picture, or this is a server you reach from another screen and you accept no local display.' },
      { id: 'g8', name: 'About 8 GB card', watts: 200, plain: 'Older and mid games, light picture work. This checker plans 200 W. Read the card page.' },
      { id: 'g12', name: 'About 12 GB card', watts: 220, plain: 'A strong everyday card. This checker plans 220 W. Read the card page.' },
      { id: 'g16', name: 'About 16 GB card', watts: 320, plain: 'High settings and heavier picture work. This checker plans 320 W.' },
      { id: 'g24', name: 'About 24 GB card', watts: 450, plain: 'A very large card. This checker plans 450 W so the power supply is not too small. Read the card page. Real cards differ.' }
    ],
    ssd: [
      { id: 'ssd-500', name: '500 GB SSD', plain: 'The system and a few apps. Not a movie shelf.' },
      { id: 'ssd-1000', name: '1 TB SSD', plain: 'System, apps, and some games.' },
      { id: 'ssd-2000', name: '2 TB SSD', plain: 'System and a large game library. Movies still belong on a hard drive.' }
    ],
    hdd: [
      { id: 'hdd-none', name: 'No hard drive yet', plain: 'Fine for a first desk. Add one when the files need a home.' },
      { id: 'hdd-4', name: 'About 4 TB hard drive', plain: 'A starter photo pile or a small movie shelf.' },
      { id: 'hdd-8', name: 'About 8 TB hard drive', plain: 'Family movies or a big camera archive.' },
      { id: 'hdd-16', name: '16 TB or more', plain: 'Media-server size. One disk is still not a backup.' }
    ],
    psu: [
      { id: 'p550', name: '550 W', watts: 550, plain: 'Calm desk, no big card.' },
      { id: 'p650', name: '650 W', watts: 650, plain: 'A normal card and a normal chip.' },
      { id: 'p750', name: '750 W', watts: 750, plain: 'Room for a stronger card.' },
      { id: 'p850', name: '850 W', watts: 850, plain: 'A large card, with air left over.' },
      { id: 'p1000', name: '1000 W', watts: 1000, plain: 'For a very large card. Still read the card page.' }
    ],
    case: [
      { id: 'itx', name: 'Small ITX case', fits: ['itx'], plain: 'Tiny. A long card often will not fit. Measure.' },
      { id: 'matx', name: 'Micro-ATX case', fits: ['itx', 'matx'], plain: 'Fits the smaller boards. An ATX board will not.' },
      { id: 'atx', name: 'ATX mid tower', fits: ['itx', 'matx', 'atx'], plain: 'The normal tower. It can hold the smaller boards too.' }
    ]
  };

  function byId(list, id) {
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }

  function checkParts(picks) {
    picks = picks || {};
    var cpu = byId(PARTS.cpu, picks.cpu);
    var board = byId(PARTS.board, picks.board);
    var ram = byId(PARTS.ram, picks.ram);
    var gpu = byId(PARTS.gpu, picks.gpu);
    var psu = byId(PARTS.psu, picks.psu);
    var box = byId(PARTS.case, picks.case);
    var lines = [];
    if (!cpu || !board || !ram || !gpu || !psu || !box) {
      return { tone: 'wait', lines: ['Pick every part. A blank is not a yes.'] };
    }
    lines.push(cpu.socket === board.socket
      ? { tone: 'go', text: 'The processor and the motherboard use the same socket, ' + cpu.socket + '.' }
      : { tone: 'stop', text: 'The processor wants ' + cpu.socket + ' and this motherboard is ' + board.socket + '. They do not fit.' });
    lines.push(ram.ram === board.ram
      ? { tone: 'go', text: 'The memory is ' + ram.ram + ', and this motherboard takes ' + board.ram + '.' }
      : { tone: 'stop', text: 'This memory is ' + ram.ram + '. This motherboard takes ' + board.ram + '. Buy the other kind.' });
    lines.push(box.fits.indexOf(board.form) !== -1
      ? { tone: 'go', text: 'The motherboard fits this case.' }
      : { tone: 'stop', text: 'This motherboard is too big for this case.' });
    var need = cpu.watts + gpu.watts + 150;
    if (psu.watts >= need + 100) {
      lines.push({ tone: 'go', text: 'The power supply has room. The plan uses about ' + need + ' W before extra headroom, and this unit is ' + psu.watts + ' W.' });
    } else if (psu.watts >= need) {
      lines.push({ tone: 'wait', text: 'The power supply can cover about ' + need + ' W on paper. A bigger unit is calmer.' });
    } else {
      lines.push({ tone: 'stop', text: 'The power supply is ' + psu.watts + ' W. This pile wants about ' + need + ' W before you add more.' });
    }
    if (gpu.watts > 0 && box.id === 'itx') {
      lines.push({ tone: 'wait', text: 'A small case and a graphics card need a length check. Read both product pages before you buy.' });
    }
    if (gpu.id === 'none' && !cpu.igpu) {
      lines.push({ tone: 'stop', text: 'This processor does not make a picture by itself. Add a graphics card, or pick a chip with graphics built in.' });
    } else if (gpu.id === 'none') {
      lines.push({ tone: 'go', text: 'No extra card. This processor can make a picture on its own.' });
    }
    if (picks.system === 'server' && gpu.watts >= 320) {
      lines.push({ tone: 'wait', text: 'A closet server rarely needs a card this large. Games and editing belong on the desk. A smaller card can still convert video.' });
    }
    var ssd = byId(PARTS.ssd, picks.ssd);
    var hdd = byId(PARTS.hdd, picks.hdd);
    if (ssd) lines.push({ tone: 'go', text: 'The boot disk is an SSD. That is where the system should live.' });
    if (hdd && hdd.id === 'hdd-none' && picks.system === 'server') {
      lines.push({ tone: 'wait', text: 'A server that keeps files wants a hard drive. The SSD is the system, not the movie shelf.' });
    } else if (hdd && hdd.id !== 'hdd-none') {
      lines.push({ tone: 'go', text: 'The hard drive is the pile. It does not have to match the processor brand.' });
    }
    var tone = 'go';
    lines.forEach(function (line) {
      if (line.tone === 'stop') tone = 'stop';
      else if (line.tone === 'wait' && tone !== 'stop') tone = 'wait';
    });
    return { tone: tone, lines: lines };
  }

  function gpuClassId(gpu) {
    var n = Number(gpu);
    if (!n) return 'none';
    if (n <= 8) return 'g8';
    if (n <= 12) return 'g12';
    if (n <= 16) return 'g16';
    return 'g24';
  }

  function suggestFit(answers, raid) {
    var a = answers || {};
    if (a.side === 'mac') {
      return {
        tone: 'wait',
        lines: [{ tone: 'wait', text: 'A Mac does not use this PC socket checker. The memory is the unified pool you already picked.' }],
        cpu: null
      };
    }
    var ramKey = Number(a.ram) >= 96 ? 'd5-96' : (Number(a.ram) >= 64 ? 'd5-64' : (Number(a.ram) >= 32 ? 'd5-32' : 'd4-16'));
    var ram = byId(PARTS.ram, ramKey);
    var gpu = byId(PARTS.gpu, gpuClassId(a.gpu));
    var ddr5 = ram.ram === 'DDR5';
    var cpu = byId(PARTS.cpu, ddr5 ? (Number(a.ram) >= 64 ? 'r7-7700' : 'r5-7600') : (gpu.id === 'none' ? 'r5-5600g' : 'r5-5600'));
    var board = byId(PARTS.board, ddr5 ? 'b650' : 'b550-atx');
    var box = byId(PARTS.case, 'atx');
    var need = cpu.watts + gpu.watts + 150;
    var psu = PARTS.psu.slice().sort(function (left, right) { return left.watts - right.watts; }).filter(function (item) {
      return item.watts >= need + 100;
    })[0] || PARTS.psu[PARTS.psu.length - 1];
    var report = checkParts({
      cpu: cpu.id, board: board.id, ram: ram.id, gpu: gpu.id, psu: psu.id, case: box.id,
      system: (a.role === 'server' || a.role === 'both') ? 'server' : 'desk'
    });
    var disks = (raid && raid.disks) || 1;
    var extra = [];
    if (disks >= 4) {
      extra.push({ tone: 'wait', text: 'Four data disks need four SATA ports, or an HBA in a PCIe slot. This suggestion is an ATX board so that slot has a place. Count the SATA ports on the board page before you skip the HBA.' });
    } else {
      extra.push({ tone: 'go', text: disks + ' data disk' + (disks === 1 ? '' : 's') + ' fit the SATA ports on a normal ATX board.' });
    }
    var fastNic = Number(a.storage) >= 8000 && (a.role === 'server' || a.role === 'both') && !hasJob(a, 'smart');
    var slots = (gpu.id === 'none' ? 0 : 1) + (disks >= 4 ? 1 : 0) + (fastNic ? 1 : 0);
    if (slots >= 3) extra.push({ tone: 'wait', text: 'A graphics card, an HBA, and a faster NIC want three slots. Confirm the board has them before you treat this as a fit.' });
    else if (gpu.id !== 'none' && disks >= 4) extra.push({ tone: 'wait', text: 'The graphics card and the HBA both want a PCIe slot. An ATX board usually has both. A mini-ITX board does not.' });
    else extra.push({ tone: 'go', text: 'No graphics card and no HBA are fighting for the same slot.' });
    if (Number(a.gpu) && Number(a.gpu) < 8) extra.push({ tone: 'wait', text: 'The card you named is smaller than 8 GB. The checker plans the 8 GB class at 200 W so the supply is not too small.' });
    if (Number(a.ram) >= 128) extra.push({ tone: 'wait', text: '128 GB is larger than the 96 GB kit in this checker. Confirm the board allows it.' });
    var lines = report.lines.concat(extra);
    var tone = report.tone;
    extra.forEach(function (line) {
      if (line.tone === 'stop') tone = 'stop';
      else if (line.tone === 'wait' && tone !== 'stop') tone = 'wait';
    });
    return { tone: tone, lines: lines, cpu: cpu, board: board, ram: ram, gpu: gpu, psu: psu, case: box };
  }

  function gpuGb(a) {
    var n = Number(a && a.gpu);
    return isFinite(n) ? n : 0;
  }

  function coverNames(a, ids) {
    return ids.filter(function (id) { return hasJob(a, id); }).map(function (id) { return JOB_LABELS[id] || id; });
  }

  function networkCovers(a) {
    var names = coverNames(a, ['smart']);
    if (a.role === 'server') names.push('A computer that stays on for the house');
    if (a.role === 'both') names.push('One computer that also runs the house');
    return names;
  }

  function storageLayers(a, storage) {
    var small = storage > 0 && storage < 1000;
    var large = storage >= 4000;
    return [
      {
        name: 'SSD and hard drive',
        lines: [
          'Two kinds of disk. Stop here if that split is enough.',
          'An SSD has no spinning head. The system and the apps live on it.',
          'A hard drive spins. Movies, photos, and the big copies live on it.',
          small
            ? 'The size you picked is a system disk. It is not the photo vault. Add a hard drive when the files need a home.'
            : 'Keep the system on an SSD. Put the pile on a hard drive.'
        ]
      },
      {
        name: 'What goes on each disk',
        lines: [
          'The operating system goes on the SSD.',
          'A player database, such as Plex or Jellyfin, goes on the SSD too. The video files do not.',
          'A game that stutters on a spinning disk belongs on the SSD.',
          'Movies, photos, and backups belong on the hard drive.',
          'One disk is not a backup. A second copy of anything you would cry about lives somewhere else.'
        ]
      },
      {
        name: 'Consider a NAS',
        lines: [
          'A NAS is a computer whose job is the disks.',
          large
            ? 'This pile is large enough to consider that separate shelf.'
            : 'This computer can hold the start. Consider a NAS when the library outgrows it, or when the disks should stay on while the desk sleeps.',
          'TrueNAS can be that computer. It is free. Unraid does a similar job and costs money.',
          'Two disks is the smallest mirror. A mirror survives one disk dying. It does not survive a fire, a theft, or a delete.',
          'The NAS stores the files. It is not the game desk, and it does not edit the video.'
        ]
      },
      {
        name: 'CMR, SMR, and the sticker',
        lines: [
          'CMR writes tracks beside each other. SMR overlaps them, so a rewrite can stall while the drive rewrites a band.',
          'Western Digital says many plain WD Red drives in the 2 TB to 6 TB sizes used SMR, and that a ZFS rebuild does not give an SMR drive the idle time it wants.',
          'WD Red Plus and WD Red Pro are the CMR NAS drives they point at. A sticker that only says Red is not enough.',
          'Purple and SkyHawk are for cameras. They are the wrong disk for a Plex library or for ZFS.',
          'Blue and Black are desktop lines. Gold is an enterprise CMR disk. IronWolf and IronWolf Pro are Seagate NAS lines. Exos is the enterprise line.',
          'Open the model datasheet and find CMR or SMR. Skip the disk if the sheet will not say.'
        ]
      },
      {
        name: 'M.2, SATA, and NVMe',
        lines: [
          'M.2 is a shape, the small gumstick connector. It is not a speed.',
          'An M.2 drive can be SATA, the same speed class as a 2.5 inch SATA SSD, or NVMe, which talks PCIe and is the fast one.',
          'A motherboard slot might accept only one of those. Read the slot.',
          'A 3.5 inch hard drive does not fit an M.2 slot. An M.2 stick does not replace a pile of movie disks.',
          'Flash wears out. The datasheet TBW number is the endurance. A disk that is rewritten all day needs a higher endurance part, not the cheapest stick.'
        ]
      },
      {
        name: 'Where to read it',
        lines: ['These are the maker pages. This page does not pick a model number for you.'],
        links: [
          { name: 'WD Red: SMR and CMR', detail: 'Western Digital’s split of Red, Red Plus, and Red Pro.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/29458' },
          { name: 'How to check CMR or SMR', detail: 'Where the datasheet says it.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/50697' },
          { name: 'WD color lines', detail: 'The marketing page. The datasheet still wins.', href: 'https://www.westerndigital.com/solutions/color-drives' }
        ]
      }
    ];
  }

  function storageCovers(a, storage) {
    var names = coverNames(a, ['files']);
    if (storage >= 4000) names.push('A large disk pile');
    return names;
  }

  function toneWord(tone) {
    if (tone === 'stop') return 'Does not fit';
    if (tone === 'wait') return 'Has a limit';
    return 'Fits';
  }

  function topicBoard(a) {
    a = a || {};
    var gpu = gpuGb(a);
    var ram = Number(a.ram) || 0;
    var storage = Number(a.storage) || 0;
    var mac = a.side === 'mac';
    var topics = [];
    function add(topic) { topics.push(topic); }
    if (hasJob(a, 'movies') || hasJob(a, 'photos') || hasJob(a, 'video')) {
      var mediaTone = 'go';
      var mediaLine = 'This computer can keep the files and play them.';
      if (hasJob(a, 'video') && !mac && gpu < 6) {
        mediaTone = 'stop';
        mediaLine = 'The card is too small to edit or convert video. Store the files here. Edit on a bigger computer.';
      } else if (hasJob(a, 'video') && !mac && gpu < 8) {
        mediaTone = 'wait';
        mediaLine = 'Light edits can work. A long 4K timeline wants a bigger card.';
      } else if (storage < 1000) {
        mediaTone = 'wait';
        mediaLine = 'The disk is small for a real library. Plan a second disk.';
      }
      add({
        id: 'media', name: 'Media', tone: mediaTone, summary: mediaLine,
        covers: coverNames(a, ['movies', 'photos', 'video']),
        get: 'A player (Jellyfin or Plex) and CMR hard drives for the files. The system and the player database go on an SSD.',
        how: 'One SSD for the system. One or more CMR disks for the library. Start with one disk you can fill, then add a second copy somewhere else.',
        look: 'CMR on the datasheet. Red Plus, Red Pro, IronWolf, or an enterprise CMR disk. Not Purple. Not a sticker that only says Red.',
        compat: 'The player and the files should be on the same machine or a fast path inside the house. Do not open the admin page to the internet.',
        buy: [
          { name: 'Jellyfin', detail: 'The free player.', href: 'https://jellyfin.org/downloads/' },
          { name: 'Plex install', detail: 'The official install note.', href: 'https://support.plex.tv/articles/200288586-installation/' }
        ],
        keys: ['plex', 'jellyfin', 'arr', 'prowlarr', 'sonarr', 'radarr']
      });
    }
    if (hasJob(a, 'ai') || hasJob(a, 'learn')) {
      var aiTone = 'go';
      var aiLine = 'Local chat fits this computer if you start with a small model.';
      if (mac) {
        if (ram < 16) { aiTone = 'stop'; aiLine = 'Under 16 GB of unified memory, skip a local chat model.'; }
        else if (ram < 32) { aiTone = 'wait'; aiLine = 'A small 7B model can run if the Mac is quiet.'; }
      } else if (gpu < 6) {
        aiTone = 'stop';
        aiLine = 'Under about 6 GB of card memory, do not plan on a useful chat model on the card.';
      } else if (gpu < 8) {
        aiTone = 'wait';
        aiLine = 'A 7B model at 4-bit can fit. Leave the bigger models for later.';
      }
      add({
        id: 'ai', name: 'AI', tone: aiTone, summary: aiLine,
        covers: coverNames(a, ['ai', 'learn']),
        get: 'Ollama, then one model that fits the card. OtaconsKeep Lite only on Windows or Ubuntu, after chat already answers.',
        how: 'One model first. A 4-bit 7B model wants about 6 GB. Do not download three models on the first day.',
        look: 'The size in the model name, and the card memory. Q4 is the smaller copy. Temperature and the system prompt do not add memory.',
        compat: 'One heavy job at a time. A game and a model fight over the same card. A Mac does not use CUDA guides.',
        buy: [
          { name: 'Ollama', detail: 'The chat runtime.', href: 'https://ollama.com/download' },
          { name: 'Ollama library', detail: 'Models you can pull. Match the size to the card.', href: 'https://ollama.com/library' }
        ],
        keys: ['ollama', 'adam', 'softmax', 'modelfile', 'gpu', 'otaconskeep', 'premium', 'piper', 'sampling']
      });
    }
    if (hasJob(a, 'games')) {
      var gameTone = 'go';
      var gameLine = 'This desk can be the game machine.';
      if (a.role === 'server') {
        gameTone = 'stop';
        gameLine = 'A closet server is the wrong box for games. Play on a desk.';
      } else if (a.side === 'linux' && a.games === 'aaa') {
        gameTone = 'wait';
        gameLine = 'New anti-cheat games may refuse Linux. Check the game before you blame the card.';
      } else if (mac) {
        gameTone = 'wait';
        gameLine = 'Some PC games have no Mac version. Anti-cheat games often do not show up here.';
      } else if (!mac && gpu < 4) {
        gameTone = 'wait';
        gameLine = 'This card is for older games at low settings.';
      }
      add({
        id: 'games', name: 'Games', tone: gameTone, summary: gameLine,
        covers: coverNames(a, ['games']),
        get: a.side === 'linux' ? 'Steam, then Valve Proton. The NVIDIA image only if the card is NVIDIA.' : 'Steam or the store the game comes from. Proton is for Linux, not for this Windows or Mac desk.',
        how: 'Install one store. Try one game. Add a second store later.',
        look: 'ProtonDB and AreWeAntiCheatYet for a Linux game. The card memory for the settings you want.',
        compat: 'Proton does not add video memory. Kernel anti-cheat stays on Windows.',
        buy: [
          { name: 'ProtonDB', detail: 'Crowd reports. Read the date.', href: 'https://www.protondb.com/' },
          { name: 'AreWeAntiCheatYet', detail: 'Which games have no Linux path.', href: 'https://areweanticheatyet.com/' }
        ],
        keys: ['proton', 'driver', 'bazzite', 'nouveau']
      });
    }
    if (hasJob(a, 'smart') || a.role === 'server' || a.role === 'both') {
      add({
        id: 'network', name: 'Network', tone: 'go', summary: 'Keep admin pages on the house network. Split guests and cameras when you are ready.',
        covers: networkCovers(a),
        get: 'A gateway you already understand, then a managed switch only on links that carry more than one VLAN.',
        how: 'Four names on paper: people, servers, cameras, guests. One VLAN number each.',
        look: 'PoE watts if a camera or access point needs power from the switch. The total budget is not max-per-port times every port.',
        compat: 'An unmanaged switch must not sit on a trunk. Do not forward Proxmox, the NAS, or Home Assistant to the internet.',
        buy: [
          { name: 'UDM Pro tech specs', detail: 'What that gateway lists today. Read the page for the unit you buy.', href: 'https://techspecs.ui.com/unifi/cloud-gateways/udm-pro' }
        ],
        keys: ['vlan', 'poe', 'lacp', 'home assistant', 'switch', 'load balancing']
      });
    }
    if (hasJob(a, 'files') || storage >= 4000) {
      add({
        id: 'storage', name: 'Storage', tone: storage >= 1000 ? 'go' : 'wait',
        summary: storage >= 4000 ? 'The disk pile is big enough to treat as its own job.' : 'You asked for files. Give them a disk that is not the only copy.',
        covers: storageCovers(a, storage),
        layers: storageLayers(a, storage),
        keys: ['nas', 'cmr', 'smr', 'm.2']
      });
    }
    if (!topics.length) {
      add({
        id: 'learn', name: 'Learning', tone: 'go', summary: 'Start with the system this build named. Add one app after it boots.',
        covers: ['The system this build named'],
        get: 'The operating system from the steps above, then one app.',
        how: 'One install. One reboot. One app.',
        look: 'The official download for that app. Skip a random script.',
        compat: 'Do not open an admin page to the internet while you are still learning the buttons.',
        buy: [{ name: 'Ollama', detail: 'A calm first app if this desk will try local chat.', href: 'https://ollama.com/download' }],
        keys: []
      });
    }
    return { topics: topics, extras: addOnAids(a) };
  }

  function addOnAids(a) {
    var media = hasJob(a, 'movies') || hasJob(a, 'photos') || hasJob(a, 'video');
    var pile = hasJob(a, 'files') || Number(a.storage) >= 4000;
    var server = a.role === 'server' || a.role === 'both';
    return [
      {
        name: 'NAS',
        summary: pile
          ? 'You already have a pile. This is the help for the shelf: why it helps, how to hook it in, and how to judge the price.'
          : 'Not required to boot. Open it when the files outgrow this computer.',
        layers: [
          {
            name: 'Why it helps',
            lines: [
              media
                ? 'You asked for a library. The desk can edit and play. The NAS holds the files and stays on when the desk sleeps, so the TV plays from the shelf.'
                : 'A NAS is a computer whose only job is the disks. The desk stays the computer you sit at.',
              'It helps because one machine no longer has to be the game desk, the chat box, and the movie shelf.',
              pile
                ? 'This build already has a pile, so the shelf is the next piece, not a someday idea.'
                : 'It does not help yet if you only have a system disk and no files. Wait until there is a pile.'
            ]
          },
          {
            name: 'How to hook it in',
            lines: [
              'Put the NAS on the same house network as the desk and the TV. Do not forward its admin page to the internet.',
              'Install the NAS system on an SSD. Put movies and photos on CMR hard drives. The player database stays on the SSD.',
              'Share one folder. Point Plex or Jellyfin at that folder. Get one file playing before you turn automatic downloads on.',
              'Two disks is the smallest mirror. A mirror survives one disk dying. It does not survive a fire, a theft, or a delete. Keep a second copy somewhere else.',
              server
                ? 'This build already stays on. The NAS can be a guest on that server, or its own small box. The disks are still not the game desk.'
                : 'Leave the desk as the computer you sit at. The NAS is the other box.'
            ]
          },
          {
            name: 'Best price, and why',
            lines: [
              'The best price is the cheapest disk that is still CMR, not the lowest sticker in the aisle.',
              'A plain WD Red in the 2 TB to 6 TB sizes was often SMR. SMR is cheaper because a rewrite can stall. Western Digital says a ZFS rebuild does not give that drive the idle time it wants. That discount is how the price goes wrong.',
              'Compare Red Plus, Red Pro, IronWolf, or an enterprise CMR disk. Same model, new, on PCPartPicker. Used is a fair price only when the listing shows the drive is healthy.',
              'Jawa is for a used small PC that can become the NAS computer. It does not tell you if the disk is CMR. Read the disk datasheet either way.',
              'Two modest CMR disks beat one giant disk. One disk is still one copy. This page does not invent a dollar amount.'
            ],
            links: [
              { name: 'WD Red: SMR and CMR', detail: 'Why the cheaper Red is often the wrong price.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/29458' },
              { name: 'How to check CMR or SMR', detail: 'Confirm the disk before you pay.', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/50697' },
              { name: 'NAS hard drives on PCPartPicker', detail: 'New prices. Still match the CMR names above.', href: 'https://pcpartpicker.com/search/?q=NAS%20hard%20drive' },
              { name: 'Jawa', detail: 'Used small PCs. Search there, then read the disk sheet.', href: 'https://www.jawa.gg/' }
            ]
          }
        ]
      },
      {
        name: 'UPS',
        summary: server
          ? 'This build stays on. A battery is the help for a power blink during a disk write.'
          : 'Put the battery on the machine that holds the files, not on the lamp.',
        layers: [
          {
            name: 'Why it helps',
            lines: [
              'A power blink in the middle of a disk write can corrupt the copy you cannot replace. The battery buys time to shut the machine down.',
              server
                ? 'This computer is meant to stay on, so the battery belongs on this build.'
                : 'The desk can wait. The battery belongs on the server or the NAS, once that box exists.',
              'A surge strip stops a spike. It does not keep the disks spinning. That is the difference.'
            ]
          },
          {
            name: 'How to hook it in',
            lines: [
              'Plug the UPS into the wall. Plug the computer and the disk shelf into the battery outlets, not the surge-only outlets.',
              'Leave lamps and chargers off the battery side. They steal the minutes you needed for the shutdown.',
              'The battery already helps before any software is installed. You can shut the machine down by hand.',
              'Install the vendor shutdown tool after that, so a long outage can turn the computer off for you. The tool is the extra. The battery outlets are the hookup.'
            ]
          },
          {
            name: 'Best price, and why',
            lines: [
              'The best price is the smallest unit that still covers the computer and the disks, not a whole-house battery.',
              'Read the watt number on the UPS and the watt number on the computer power supply. The UPS has to be able to carry that supply. A cheaper box with only surge outlets does not keep the machine up, so it is not cheaper in the way that matters.',
              'A low price that hides a tiny battery is the wrong bargain. The watt number and the count of battery outlets have to be on the same page as the price.',
              'This page does not invent a dollar amount. Compare those two numbers, then read the live price.'
            ],
            links: [
              { name: 'UPS units on PCPartPicker', detail: 'Live prices. Check watts and battery outlets on the same page.', href: 'https://pcpartpicker.com/search/?q=UPS' }
            ]
          }
        ]
      },
      {
        name: 'Managed switch',
        summary: server
          ? 'The help for splitting people, cameras, and guests onto different networks.'
          : 'You probably do not need this yet. Open it before you buy a smart switch you will not use.',
        layers: [
          {
            name: 'Why it helps',
            lines: [
              server
                ? 'A server build grows cameras and guests. A managed switch is how one cable carries more than one network without mixing them.'
                : 'A flat house, one network, does not need a managed switch. An unmanaged switch is the right tool until a camera or a guest network shows up.',
              'It helps when people, cameras, and guests must not see each other. Creating a VLAN on paper does not isolate them. The switch and the gateway both have to agree.',
              'It does not help a desk that only talks to the router. Buying it early spends money on ports you will not configure.'
            ]
          },
          {
            name: 'How to hook it in',
            lines: [
              'The gateway creates the networks. The switch carries them. A trunk is the cable that carries more than one. Both ends must agree, or the network falls over.',
              'Do not plug a trunk into an unmanaged switch. That switch will mishandle the tags.',
              'Access ports are the normal ports: one network, untagged. Cameras go on the camera network. The desk stays on the trusted network.',
              'PoE is power from the switch. Use it only when a camera or an access point needs it. Add the device watts. The switch budget is not the maximum per port times every port.',
              'Do not forward the server, the NAS, or Home Assistant to the internet. The switch stays inside the house.'
            ]
          },
          {
            name: 'Best price, and why',
            lines: [
              'The best price is the smallest managed switch with enough ports for the devices you have, plus two spare.',
              'PoE raises the price. Pay for it only when a camera or an access point takes power from the switch. A 48-port switch is a bad price for a handful of cables.',
              'If you still have one flat network, the unmanaged switch is the better price. The managed one is the better price only after you actually split networks.',
              'Read VLAN support and the PoE budget on the spec page, next to the price. This page does not invent a dollar amount.'
            ],
            links: [
              { name: 'Managed switches on PCPartPicker', detail: 'Live prices. Match the port count and PoE only if you need power.', href: 'https://pcpartpicker.com/search/?q=managed%20switch' }
            ]
          }
        ]
      }
    ];
  }

  function mount(rootEl) {
    var answers = {};
    var index = 0;
    var labNotes = null;
    try {
      var savedLab = localStorage.getItem('otacon-lab-build-v1');
      if (savedLab) {
        var savedData = JSON.parse(savedLab);
        if (savedData && savedData.version === 1 && savedData.answers && typeof savedData.answers === 'object') {
          answers = savedData.answers;
          index = 999;
        }
      }
    } catch (err) { /* a bad save just starts the questionnaire */ }

    function el(tag, className, text) {
      var node = document.createElement(tag);
      if (className) node.className = className;
      if (text) node.textContent = text;
      return node;
    }

    function draw() {
      rootEl.innerHTML = '';
      var steps = stepsFor(answers);
      if (index >= steps.length) return drawResult();
      var step = steps[index];
      var choices = field(step, answers, 'choices') || [];
      rootEl.appendChild(el('p', 'wiz-progress', 'Layer ' + (index + 1) + ' of ' + steps.length));
      rootEl.appendChild(el('h2', 'wiz-title', field(step, answers, 'title')));
      rootEl.appendChild(el('p', 'wiz-hint', field(step, answers, 'hint') || ''));
      var list = el('div', 'wiz-choices');
      var picked = Array.isArray(answers[step.id]) ? answers[step.id] : [];
      choices.forEach(function (choice) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'wiz-choice' + (step.multi ? ' wiz-multi' : '');
        button.setAttribute('aria-pressed', 'false');
        var on = step.multi
          ? picked.indexOf(choice.value) !== -1
          : String(answers[step.id]) === String(choice.value);
        if (on) {
          button.classList.add('is-on');
          button.setAttribute('aria-pressed', 'true');
        }
        button.appendChild(el('strong', '', (on && step.multi ? 'Yes · ' : '') + choice.label));
        button.appendChild(el('span', '', choice.detail));
        button.addEventListener('click', function () {
          if (step.multi) {
            var current = Array.isArray(answers[step.id]) ? answers[step.id].slice() : [];
            var at = current.indexOf(choice.value);
            if (at === -1) current.push(choice.value);
            else current.splice(at, 1);
            answers[step.id] = current;
            if (current.indexOf('games') === -1) delete answers.games;
            draw();
            return;
          }
          answers[step.id] = choice.value;
          index += 1;
          draw();
        });
        list.appendChild(button);
      });
      rootEl.appendChild(list);
      if (step.multi) {
        var keep = document.createElement('button');
        keep.type = 'button';
        keep.className = 'btn btn-primary wiz-next';
        keep.textContent = 'Continue';
        keep.disabled = picked.length === 0;
        keep.addEventListener('click', function () {
          if (!Array.isArray(answers[step.id]) || !answers[step.id].length) return;
          index += 1;
          draw();
        });
        rootEl.appendChild(keep);
      }
      if (index > 0) {
        var back = document.createElement('button');
        back.type = 'button';
        back.className = 'btn btn-ghost wiz-back';
        back.textContent = 'Back';
        back.addEventListener('click', function () {
          index -= 1;
          draw();
        });
        rootEl.appendChild(back);
      }
    }

    function claimLessons(report, topics) {
      var pool = (report.plan.lessons || []).concat(report.plan.advanced || []);
      var used = {};
      topics.forEach(function (topic) {
        topic.lessons = [];
        pool.forEach(function (item, index) {
          if (used[index]) return;
          var title = String(item.title || '').toLowerCase();
          var hit = (topic.keys || []).some(function (key) { return title.indexOf(key) !== -1; });
          if (hit) {
            used[index] = true;
            topic.lessons.push(item);
          }
        });
      });
    }

    function labeledLine(title, text) {
      var row = el('p', '');
      var strong = document.createElement('strong');
      strong.textContent = title;
      row.appendChild(strong);
      row.appendChild(document.createTextNode(' ' + text));
      return row;
    }

    function detailBlock(item) {
      var box = el('div', 'wiz-detail');
      box.appendChild(labeledLine('What to get.', item.get));
      box.appendChild(labeledLine('How much.', item.how));
      box.appendChild(labeledLine('What to look for.', item.look));
      box.appendChild(labeledLine('Compatibility.', item.compat));
      if (item.buy && item.buy.length) {
        var ul = document.createElement('ul');
        item.buy.forEach(function (link) {
          var li = document.createElement('li');
          var anchor = document.createElement('a');
          anchor.href = link.href;
          anchor.textContent = link.name;
          anchor.target = '_blank';
          anchor.rel = 'noopener';
          li.appendChild(anchor);
          if (link.detail) li.appendChild(document.createTextNode('. ' + link.detail));
          ul.appendChild(li);
        });
        box.appendChild(ul);
      }
      (item.lessons || []).forEach(function (lesson) {
        box.appendChild(lessonSection(lesson));
      });
      return box;
    }

    function linkList(links) {
      var ul = document.createElement('ul');
      (links || []).forEach(function (link) {
        var li = document.createElement('li');
        var anchor = document.createElement('a');
        anchor.href = link.href;
        anchor.textContent = link.name;
        anchor.target = '_blank';
        anchor.rel = 'noopener';
        li.appendChild(anchor);
        if (link.detail) li.appendChild(document.createTextNode('. ' + link.detail));
        ul.appendChild(li);
      });
      return ul;
    }

    function layerStack(topic) {
      var layers = topic.layers || [];
      function build(i) {
        var wrap = el('div', '');
        if (i >= layers.length) return wrap;
        var layer = layers[i];
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-ghost';
        button.textContent = 'Layer ' + (i + 2) + '. ' + layer.name;
        button.setAttribute('aria-expanded', 'false');
        var slot = el('div', 'wiz-layer');
        var open = false;
        button.addEventListener('click', function () {
          open = !open;
          slot.textContent = '';
          button.setAttribute('aria-expanded', open ? 'true' : 'false');
          if (!open) return;
          (layer.lines || []).forEach(function (line) {
            slot.appendChild(el('p', '', line));
          });
          if (layer.links && layer.links.length) slot.appendChild(linkList(layer.links));
          if (i === layers.length - 1) {
            (topic.lessons || []).forEach(function (lesson) {
              slot.appendChild(lessonSection(lesson));
            });
          } else {
            slot.appendChild(build(i + 1));
          }
          return;
        });
        wrap.appendChild(button);
        wrap.appendChild(slot);
        return wrap;
      }
      return build(0);
    }

    function aidDiagram(extras) {
      var root = el('div', 'wiz-tree');
      var head = el('section', 'wiz-node is-done');
      head.appendChild(el('h3', '', 'Consider adding'));
      head.appendChild(el('p', '', 'Click a piece. Three branches drop under it. Click a branch to open the note. Click that same branch again to close it.'));
      root.appendChild(head);
      extras.forEach(function (item) {
        root.appendChild(el('div', 'wiz-stem'));
        var piece = document.createElement('button');
        piece.type = 'button';
        piece.className = 'wiz-node';
        piece.setAttribute('aria-expanded', 'false');
        piece.appendChild(el('strong', '', item.name));
        piece.appendChild(el('span', '', item.summary));
        var kids = el('div', 'wiz-kids');
        kids.hidden = true;
        var pieceOpen = false;
        (item.layers || []).forEach(function (layer) {
          var row = el('div', 'wiz-kid');
          row.appendChild(el('div', 'wiz-elbow'));
          var branch = document.createElement('button');
          branch.type = 'button';
          branch.className = 'wiz-node';
          branch.setAttribute('aria-expanded', 'false');
          branch.appendChild(el('strong', '', layer.name));
          var detail = el('div', 'wiz-kid');
          detail.hidden = true;
          var note = el('div', 'wiz-node is-now');
          (layer.lines || []).forEach(function (line) { note.appendChild(el('p', '', line)); });
          if (layer.links && layer.links.length) note.appendChild(linkList(layer.links));
          detail.appendChild(el('div', 'wiz-elbow'));
          detail.appendChild(note);
          var branchOpen = false;
          branch.addEventListener('click', function () {
            branchOpen = !branchOpen;
            branch.classList.toggle('is-on', branchOpen);
            branch.setAttribute('aria-expanded', branchOpen ? 'true' : 'false');
            detail.hidden = !branchOpen;
          });
          row.appendChild(branch);
          kids.appendChild(row);
          kids.appendChild(detail);
        });
        piece.addEventListener('click', function () {
          pieceOpen = !pieceOpen;
          piece.classList.toggle('is-on', pieceOpen);
          piece.setAttribute('aria-expanded', pieceOpen ? 'true' : 'false');
          kids.hidden = !pieceOpen;
        });
        root.appendChild(piece);
        root.appendChild(kids);
      });
      return root;
    }

    function moreButton(item) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-ghost';
      button.textContent = 'I need more detail';
      var open = false;
      var slot = el('div', '');
      button.addEventListener('click', function () {
        open = !open;
        slot.textContent = '';
        if (open) slot.appendChild(detailBlock(item));
      });
      var wrap = el('div', '');
      wrap.appendChild(button);
      wrap.appendChild(slot);
      return wrap;
    }

    function fillSelect(select, list) {
      var blank = document.createElement('option');
      blank.value = '';
      blank.textContent = 'Choose';
      select.appendChild(blank);
      list.forEach(function (item) {
        var option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name;
        select.appendChild(option);
      });
    }

    function priceBlock(notes) {
      var box = el('div', '');
      var checked = notes && notes.checked ? notes.checked : 'the links below';
      box.appendChild(el('p', '', 'This month’s prices live on the source sites. This page does not invent a dollar amount. The links were confirmed ' + checked + '.'));
      var sources = (notes && notes.prices && notes.prices.sources) || [
        { name: 'Jawa', href: 'https://www.jawa.gg/', detail: 'Used graphics cards and used whole PCs.' },
        { name: 'PCPartPicker', href: 'https://pcpartpicker.com/', detail: 'New parts and a running total.' }
      ];
      var ul = document.createElement('ul');
      sources.forEach(function (link) {
        var li = document.createElement('li');
        var anchor = document.createElement('a');
        anchor.href = link.href;
        anchor.textContent = link.name;
        anchor.target = '_blank';
        anchor.rel = 'noopener';
        li.appendChild(anchor);
        if (link.detail) li.appendChild(document.createTextNode('. ' + link.detail));
        ul.appendChild(li);
      });
      box.appendChild(ul);
      var builds = (notes && notes.prices && notes.prices.builds) || [];
      builds.forEach(function (build) {
        box.appendChild(el('p', '', build.name + '. ' + build.for + ' ' + build.parts + ' ' + build.check));
      });
      var ltt = (notes && notes.ltt) || [];
      if (ltt.length) {
        box.appendChild(el('p', '', 'Recent Linus Tech Tips videos. Background notes, not a shopping list.'));
        var videos = document.createElement('ul');
        ltt.slice(0, 3).forEach(function (video) {
          var li = document.createElement('li');
          var anchor = document.createElement('a');
          anchor.href = video.href;
          anchor.textContent = video.title;
          anchor.target = '_blank';
          anchor.rel = 'noopener';
          li.appendChild(anchor);
          videos.appendChild(li);
        });
        box.appendChild(videos);
      }
      return box;
    }

    function partChoices(state, id) {
      var cpu = byId(PARTS.cpu, state.cpu);
      var board = byId(PARTS.board, state.board);
      if (id === 'system') {
        return [
          { id: 'desk', name: 'A desk PC', plain: 'You sit at it. Games, school, photos, and a normal screen.' },
          { id: 'server', name: 'A server', plain: 'It stays on for the house. Files, movies, and house apps.' },
          { id: 'unsure', name: 'I am not sure', plain: 'Start as a desk PC. You can still add disks and leave it on later.' }
        ];
      }
      if (id === 'maker') {
        return [
          { id: 'amd', name: 'AMD', plain: 'One of the two companies that make the processor. These chips use AM4 or AM5.' },
          { id: 'intel', name: 'Intel', plain: 'The other company. The chips in this list use LGA1700.' },
          { id: 'either', name: 'I do not know what that means', plain: 'That is fine. The next block explains it and shows both.' }
        ];
      }
      if (id === 'cpu') {
        return PARTS.cpu.filter(function (item) {
          return state.maker === 'either' || !state.maker || item.maker === state.maker;
        });
      }
      if (id === 'board') {
        return PARTS.board.filter(function (item) { return cpu && item.socket === cpu.socket; });
      }
      if (id === 'ram') {
        return PARTS.ram.filter(function (item) { return board && item.ram === board.ram; });
      }
      if (id === 'gpu') return PARTS.gpu;
      if (id === 'ssd') return PARTS.ssd;
      if (id === 'hdd') return PARTS.hdd;
      if (id === 'psu') return PARTS.psu;
      if (id === 'case') return PARTS.case;
      return [];
    }

    function pcPanel() {
      var state = {};
      var order = ['system', 'maker', 'cpu', 'board', 'ram', 'gpu', 'ssd', 'hdd', 'psu', 'case'];
      var meta = {
        system: { depth: 0, title: '1. The system', hint: 'This is the whole computer. Everything else hangs under it.' },
        maker: { depth: 1, title: '2. Who makes the brain', hint: 'AMD and Intel both make the processor. The motherboard has to be the same side. You cannot mix them.' },
        cpu: { depth: 2, title: '3. The processor', hint: 'The brain. These are common chips, not every chip on earth. Match the socket if yours is missing.' },
        board: { depth: 2, title: '4. The motherboard', hint: 'Only boards that fit the processor you just picked.' },
        ram: { depth: 2, title: '5. The memory', hint: 'Only the memory type that board accepts. DDR4 and DDR5 do not swap.' },
        gpu: { depth: 1, title: '6. Graphics', hint: 'The picture card. Skip it only when the processor can draw the screen itself.' },
        ssd: { depth: 1, title: '7. Storage, the SSD', hint: 'The fast disk. The system and the apps live here.' },
        hdd: { depth: 2, title: '8. Storage, the hard drive', hint: 'The spinning disk for movies, photos, and backups. A different shape from the SSD.' },
        psu: { depth: 1, title: '9. Power', hint: 'The supply has to cover the processor and the card, with air left over.' },
        case: { depth: 1, title: '10. The case', hint: 'The box has to be big enough for the motherboard.' }
      };
      var box = el('div', '');
      box.appendChild(el('p', '', 'The first block is the whole computer. Each block under it is one piece. Closed blocks wait. Green means that piece fits the one above it.'));

      function currentId() {
        for (var i = 0; i < order.length; i++) if (!state[order[i]]) return order[i];
        return '';
      }

      function drawChoices(node, id) {
        var list = el('div', 'wiz-choices');
        partChoices(state, id).forEach(function (choice) {
          var button = document.createElement('button');
          button.type = 'button';
          button.className = 'wiz-choice';
          button.appendChild(el('strong', '', choice.name));
          if (choice.plain) button.appendChild(el('span', '', choice.plain));
          button.addEventListener('click', function () {
            state[id] = choice.id;
            var from = order.indexOf(id);
            order.slice(from + 1).forEach(function (key) {
              if (key === 'board' || key === 'ram' || key === 'cpu') delete state[key];
            });
            if (id === 'maker') delete state.cpu;
            if (id === 'cpu') { delete state.board; delete state.ram; }
            if (id === 'board') delete state.ram;
            redraw();
          });
          list.appendChild(button);
        });
        node.appendChild(list);
      }

      function redraw() {
        var tree = box.querySelector('.wiz-tree');
        if (tree) tree.remove();
        tree = el('div', 'wiz-tree');
        var here = currentId();
        order.forEach(function (id) {
          var info = meta[id];
          var pool = (id === 'system' || id === 'maker') ? partChoices(state, id) : (PARTS[id] || []);
          var picked = byId(pool, state[id]);
          var node = el('section', 'wiz-node wiz-depth-' + info.depth + (state[id] ? ' is-done' : (id === here ? ' is-now' : ' is-wait')));
          node.appendChild(el('h3', '', info.title));
          if (state[id] && picked) {
            node.appendChild(el('p', '', picked.name));
            var change = document.createElement('button');
            change.type = 'button';
            change.className = 'btn btn-ghost';
            change.textContent = 'Change this block';
            change.addEventListener('click', function () {
              var from = order.indexOf(id);
              order.slice(from).forEach(function (key) { delete state[key]; });
              redraw();
            });
            node.appendChild(change);
          } else if (id === here) {
            node.appendChild(el('p', '', info.hint));
            if (id === 'maker' || (id === 'cpu' && state.maker === 'either')) {
              node.appendChild(el('p', '', 'AMD and Intel are companies, not socket types. The socket is the shape on the board. AM4 and AM5 are AMD. LGA1700 in this list is Intel.'));
            }
            drawChoices(node, id);
          } else {
            node.appendChild(el('p', '', 'Closed until the block above is chosen.'));
          }
          if (id !== 'system') tree.appendChild(el('div', 'wiz-stem wiz-depth-' + info.depth));
          tree.appendChild(node);
        });
        if (!here) {
          var report = checkParts(state);
          var done = el('section', 'wiz-node is-now');
          var word = report.tone === 'go' ? 'Fits' : (report.tone === 'stop' ? 'Does not fit' : 'Check one limit');
          done.appendChild(el('h3', '', '11. Does this pile fit?'));
          var banner = el('div', 'wiz-check ' + report.tone);
          banner.appendChild(el('strong', '', word));
          report.lines.forEach(function (line) {
            var text = typeof line === 'string' ? line : line.text;
            var tone = typeof line === 'string' ? report.tone : line.tone;
            var row = el('p', '', text);
            if (tone === 'stop') row.style.color = '#ef5f6b';
            else if (tone === 'wait') row.style.color = '#e0a83c';
            else row.style.color = '#43d98a';
            banner.appendChild(row);
          });
          banner.appendChild(el('p', '', 'Your exact part may be missing. Match three things: the socket, DDR4 or DDR5, and the case size. Then size the power supply to the card.'));
          done.appendChild(banner);
          tree.appendChild(el('div', 'wiz-stem'));
          tree.appendChild(done);
          var prices = el('section', 'wiz-node is-now');
          prices.appendChild(el('h3', '', '12. Best prices'));
          prices.appendChild(el('p', '', 'Last step. The live prices are on the seller sites. This page does not invent a dollar amount.'));
          var ul = document.createElement('ul');
          order.forEach(function (id) {
            var item = byId(PARTS[id] || [], state[id]);
            if (!item) return;
            var li = document.createElement('li');
            var anchor = document.createElement('a');
            anchor.href = 'https://pcpartpicker.com/search/?q=' + encodeURIComponent(item.name);
            anchor.target = '_blank';
            anchor.rel = 'noopener';
            anchor.textContent = item.name + ' on PCPartPicker';
            li.appendChild(anchor);
            ul.appendChild(li);
          });
          var jawa = document.createElement('li');
          var jawaLink = document.createElement('a');
          jawaLink.href = 'https://www.jawa.gg/';
          jawaLink.target = '_blank';
          jawaLink.rel = 'noopener';
          jawaLink.textContent = 'Jawa';
          jawa.appendChild(jawaLink);
          jawa.appendChild(document.createTextNode('. Used graphics cards and used whole PCs. Search the part name there.'));
          ul.appendChild(jawa);
          prices.appendChild(ul);
          prices.appendChild(priceBlock(labNotes));
          tree.appendChild(el('div', 'wiz-stem'));
          tree.appendChild(prices);
        }
        box.appendChild(tree);
      }

      redraw();
      return box;
    }

    function topicCard(topic) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'wiz-topic ' + topic.tone;
      button.appendChild(el('strong', '', topic.name));
      button.appendChild(el('span', 'wiz-verdict', toneWord(topic.tone)));
      var covers = (topic.covers || []).join(', ');
      if (covers) button.appendChild(el('span', '', 'From what you selected: ' + covers));
      button.appendChild(el('span', '', 'What you can do: ' + topic.summary));
      return button;
    }

    function topicPanel(topic) {
      var node = el('div', 'wiz-check ' + topic.tone);
      node.appendChild(el('strong', '', toneWord(topic.tone) + '. ' + topic.name));
      var covers = (topic.covers || []).join(', ');
      if (covers) node.appendChild(labeledLine('From what you selected.', covers));
      node.appendChild(labeledLine('What you can do.', topic.summary));
      if (topic.layers && topic.layers.length) {
        node.appendChild(el('p', '', 'This is the top. Open the next layer only when you want the next step. The deeper layers stay closed.'));
        node.appendChild(layerStack(topic));
      } else {
        node.appendChild(moreButton(topic));
      }
      return node;
    }

    function renderShop(report) {
      var board = topicBoard(answers);
      claimLessons(report, board.topics);
      var wrap = el('section', 'wiz-block');
      wrap.appendChild(el('h3', '', 'Here is what you can do with what you selected'));
      wrap.appendChild(el('p', '', 'Each box is a category those picks landed in. Fits means this computer can do it. Has a limit means it works with a catch. Does not fit means pick a different job for this computer, or a bigger part.'));
      var buildPanel = el('div', 'wiz-panel');
      var buildBtn = document.createElement('button');
      buildBtn.type = 'button';
      buildBtn.className = 'wiz-build';
      buildBtn.appendChild(el('strong', '', 'Help me build a PC or server'));
      buildBtn.appendChild(el('span', '', 'Start with the whole computer. Then the brain, the disks, the power, and the best prices.'));
      var row = el('div', 'wiz-topics');
      var panel = el('div', 'wiz-panel');
      var notes = null;
      var buttons = [];
      function show(button, node, target) {
        buttons.forEach(function (other) { other.classList.remove('is-on'); });
        button.classList.add('is-on');
        panel.textContent = '';
        buildPanel.textContent = '';
        (target || panel).appendChild(node);
      }
      buildBtn.addEventListener('click', function () {
        show(buildBtn, pcPanel(), buildPanel);
      });
      buttons.push(buildBtn);
      wrap.appendChild(buildBtn);
      wrap.appendChild(buildPanel);
      board.topics.forEach(function (topic) {
        var button = topicCard(topic);
        button.addEventListener('click', function () {
          show(button, topicPanel(topic));
        });
        buttons.push(button);
        row.appendChild(button);
      });
      wrap.appendChild(row);
      wrap.appendChild(panel);
      wrap.appendChild(el('h3', 'wiz-also-title', 'Also'));
      var also = el('div', 'wiz-topics');
      var extra = document.createElement('button');
      extra.type = 'button';
      extra.className = 'wiz-topic';
      extra.appendChild(el('strong', '', 'Consider adding'));
      extra.appendChild(el('span', '', 'A tree. Click a piece and three branches drop down. Click a branch again to close it.'));
      extra.addEventListener('click', function () {
        show(extra, aidDiagram(board.extras));
      });
      buttons.push(extra);
      also.appendChild(extra);
      wrap.appendChild(also);
      if (typeof fetch === 'function') {
        fetch('/classroom/modules/00-pick-your-lab/lab-notes.json').then(function (response) {
          return response.ok ? response.json() : null;
        }).then(function (data) {
          notes = data;
          labNotes = data;
        }).catch(function () { notes = null; });
      }
      return wrap;
    }

    function drawResult() {
      var report = explain(answers);
      var root = labBreakdown(answers, report);
      var openIds = [root.id];
      var focus = null;
      var cartOpen = false;
      var inspected = null;
      var record = { version: 1, name: '', items: {} };
      var STORAGE_KEY = 'otacon-lab-build-v1';

      function persist() {
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, answers: answers, name: record.name, items: record.items, switchPlan: record.switchPlan || null }));
        } catch (err) { /* private mode can refuse storage */ }
      }

      function restore() {
        try {
          var raw = localStorage.getItem(STORAGE_KEY);
          if (!raw) return;
          var data = JSON.parse(raw);
          if (!data || data.version !== 1) return;
          if (JSON.stringify(data.answers) !== JSON.stringify(answers)) return;
          record.name = data.name || '';
          record.items = data.items || {};
          record.switchPlan = data.switchPlan || null;
        } catch (err) { /* ignore a bad saved blob */ }
      }

      function commit(id, state, actual, quantity) {
        var prev = record.items[id] || { quantity: null, actual: null };
        record.items[id] = {
          state: state,
          quantity: quantity !== undefined ? quantity : (prev.quantity != null ? prev.quantity : null),
          actual: actual !== undefined ? actual : prev.actual
        };
        persist();
      }

      function itemState(id) {
        var saved = record.items[id];
        return saved && saved.state ? saved.state : '';
      }

      restore();
      persist();

      function paintLines(parent, lines) {
        (lines || []).forEach(function (line) {
          if (!line) return;
          if (line.href) {
            var row = el('p', '');
            var anchor = document.createElement('a');
            anchor.href = line.href;
            anchor.textContent = line.name;
            anchor.target = '_blank';
            anchor.rel = 'noopener';
            row.appendChild(anchor);
            if (line.detail) row.appendChild(document.createTextNode('. ' + line.detail));
            parent.appendChild(row);
          } else {
            parent.appendChild(el('p', '', String(line)));
          }
        });
      }

      function paintStudy(study) {
        var box = el('section', 'wiz-card');
        box.appendChild(el('p', 'wiz-level', 'Trade study'));
        box.appendChild(el('h2', 'wiz-title', study.title));
        box.appendChild(el('p', '', study.requirement));
        var table = document.createElement('table');
        table.className = 'wiz-study';
        var head = document.createElement('tr');
        (study.columns || ['Candidate', 'CMR', 'NAS rated', 'Warranty', 'Result']).forEach(function (label) {
          var cell = document.createElement('th');
          cell.textContent = label;
          head.appendChild(cell);
        });
        table.appendChild(head);
        study.rows.forEach(function (row) {
          var tr = document.createElement('tr');
          (row.cells || [row.name, row.cmr, row.nas, row.warranty, row.result]).forEach(function (value) {
            var cell = document.createElement('td');
            cell.textContent = value;
            tr.appendChild(cell);
          });
          table.appendChild(tr);
        });
        box.appendChild(table);
        if (study.ideal && study.ideal !== study.decision) box.appendChild(el('p', '', 'Requirements want ' + study.ideal + '. This band can buy ' + study.decision + '.'));
        box.appendChild(el('h3', '', 'Decision: ' + study.decision));
        (study.requirements || []).forEach(function (req) {
          box.appendChild(el('p', '', req.id + '  ' + req.text + '  ' + req.result));
        });
        if (study.confidence) box.appendChild(el('p', '', 'Decision confidence: ' + study.confidence));
        paintLines(box, study.why);
        if (study.forecast && study.forecast.length) {
          box.appendChild(el('h3', '', 'If you spend more'));
          study.forecast.forEach(function (rung) { box.appendChild(el('p', '', rung.line)); });
        }
        box.appendChild(el('p', '', 'Tradeoff: ' + study.tradeoff));
        box.appendChild(el('p', '', study.forecast ? 'The dollars in that ladder are class floors, dated Sep 24, 2026. They are not a live shelf price.' : 'Price checked on the seller page. This page does not invent a dollar amount.'));
        paintLines(box, study.links);
        return box;
      }

      function levelStamp(level) {
        return {
          L1: 'L1 System',
          L2: 'L2 Subsystem',
          L3: 'L3 Assembly',
          L4: 'L4 Component',
          L5: 'L5 Solution'
        }[level] || level;
      }

      function samePath(a, b) {
        if (a.length !== b.length) return false;
        for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
        return true;
      }

      function isPrefix(prefix, full) {
        if (full.length < prefix.length) return false;
        for (var i = 0; i < prefix.length; i++) if (full[i] !== prefix[i]) return false;
        return true;
      }

      function heroOrder(children, parentIds) {
        var active = -1;
        children.forEach(function (child, index) {
          if (openIds[parentIds.length] === child.id) active = index;
        });
        if (active < 0) return children;
        var rest = children.filter(function (_, index) { return index !== active; });
        var mid = Math.floor(rest.length / 2);
        return rest.slice(0, mid).concat([children[active]], rest.slice(mid));
      }

      function usable(item) {
        return item && ((item.lines && item.lines.length) || item.panel || item.study);
      }

      function drawerGroups(node) {
        var spec = {
          hardware: [['why', 'Why'], ['compare', 'Compare'], ['study', 'Trade study'], ['buy', 'Buy']],
          'free-software': [['why', 'Why'], ['install', 'Install'], ['compare', 'Compare'], ['requirements', 'Requirements']],
          'paid-software': [['why', 'Why'], ['license', 'License'], ['cost', 'Cost'], ['compare', 'Compare']],
          service: [['why', 'Why'], ['configure', 'Configure'], ['requirements', 'Requirements']],
          architecture: [['why', 'Why'], ['study', 'Trade study'], ['risks', 'Risks']],
          optional: [['add', 'Add to build'], ['skip', 'Skip']]
        }[node.kind] || [['why', 'Why'], ['install', 'Install'], ['study', 'Trade study']];
        return spec.map(function (pair) {
          var items = (node.sections || []).filter(function (item) {
            return usable(item) && (item.slot || 'why') === pair[0];
          });
          if (!items.length) return null;
          return { key: pair[0], name: items.length === 1 ? items[0].name : pair[1], items: items };
        }).filter(Boolean);
      }

      function renderDrawer(group) {
        var box = el('aside', 'wiz-drawer');
        var close = document.createElement('button');
        close.type = 'button';
        close.className = 'btn btn-ghost wiz-back';
        close.textContent = 'Close';
        close.addEventListener('click', function () {
          focus = null;
          paint();
        });
        box.appendChild(close);
        box.appendChild(el('h2', 'wiz-title', group.name));
        group.items.forEach(function (item) {
          if (item.study) {
            box.appendChild(paintStudy(item.study));
          } else if (item.panel === 'build') {
            box.appendChild(el('p', '', 'Six kinds of part, one block at a time. Prices are last, and they come from the seller.'));
            box.appendChild(pcPanel());
          } else {
            if (group.items.length > 1) box.appendChild(el('h3', '', item.name));
            paintLines(box, item.lines);
          }
        });
        return box;
      }

      function renderCol(node, ids) {
        var onPath = isPrefix(ids, openIds);
        var tip = samePath(ids, openIds);
        var col = el('div', 'wiz-col' + (onPath ? ' is-on-path' : ''));
        var tile = document.createElement('button');
        tile.type = 'button';
        tile.className = 'wiz-tile' + (onPath ? ' is-on' : '') + (tip ? ' is-tip' : '');
        tile.appendChild(el('span', 'wiz-level', levelStamp(node.level)));
        tile.appendChild(el('strong', '', node.title));
        var statusLabel = { ready: 'In the build', selected: 'Selected', recommended: 'Recommended', over: 'Over budget', need: 'Choose', skip: 'Not required' }[node.status];
        if (itemState(node.id) === 'owned') statusLabel = 'Owned';
        else if (itemState(node.id) === 'equipped') statusLabel = 'Equipped';
        else if (itemState(node.id) === 'skipped') statusLabel = 'Skipped';
        if (statusLabel) tile.appendChild(el('span', 'wiz-open', statusLabel));
        if (node.level === 'L2' && onPath && openIds.length > 1) tile.appendChild(el('span', 'wiz-open', 'Open'));
        if (node.level === 'L2' && !onPath) tile.appendChild(el('span', 'wiz-cue', 'Explore >'));
        tile.addEventListener('mousedown', function (event) { event.preventDefault(); });
        tile.addEventListener('click', function () {
          focus = null;
          inspected = node;
          if (samePath(ids, openIds)) {
            if (ids.length > 1) openIds = ids.slice(0, -1);
          } else if (isPrefix(ids, openIds)) {
            openIds = ids.length === 1 ? ids.slice() : ids.slice(0, -1);
          } else {
            openIds = ids.slice();
          }
          paint();
        });
        col.appendChild(tile);
        if (onPath && node.children && node.children.length) {
          col.appendChild(el('div', 'wiz-stem'));
          if (node.level === 'L1' && openIds.length > 1) col.appendChild(el('p', 'wiz-switch', 'Explore another subsystem'));
          var kids = heroOrder(node.children, ids);
          var row = el('div', 'wiz-row' + (kids.length > 1 ? ' is-many' : ' is-one'));
          kids.forEach(function (child) {
            var childIds = ids.concat([child.id]);
            var active = openIds.length > ids.length && openIds[ids.length] === child.id;
            var wrap = renderCol(child, childIds);
            if (openIds.length > ids.length && !active) wrap.className += ' is-peer';
            row.appendChild(wrap);
          });
          col.appendChild(row);
        }
        if (tip && (!node.children || !node.children.length)) {
          if (node.picked) col.appendChild(el('p', 'wiz-level', 'Picked'));
          if (node.line) col.appendChild(el('p', 'wiz-node-line', node.line));
          var groups = drawerGroups(node);
          if (groups.length) {
            col.appendChild(el('div', 'wiz-stem'));
            var actions = el('div', 'wiz-actions');
            groups.forEach(function (group) {
              var chip = document.createElement('button');
              chip.type = 'button';
              chip.className = 'wiz-chip' + (focus && focus.key === group.key ? ' is-on' : '');
              chip.textContent = group.name + ' >';
              chip.addEventListener('mousedown', function (event) { event.preventDefault(); });
              chip.addEventListener('click', function () {
                focus = focus && focus.key === group.key ? null : group;
                paint();
              });
              actions.appendChild(chip);
            });
            col.appendChild(actions);
          }
        }
        if (tip && node.kind === 'hardware' && node.offer) {
          var bill = el('div', 'wiz-actions');
          var onBill = itemState(node.id) === 'equipped' || itemState(node.id) === 'owned';
          var toggle = document.createElement('button');
          toggle.type = 'button';
          toggle.className = 'wiz-chip';
          toggle.textContent = onBill ? 'Remove from build' : 'Equip';
          toggle.addEventListener('click', function () {
            commit(node.id, onBill ? 'skipped' : 'equipped');
            paint();
          });
          bill.appendChild(toggle);
          var priceLabel = el('label', 'wiz-price', 'Price you saw');
          var priceInput = document.createElement('input');
          priceInput.type = 'number';
          priceInput.min = '0';
          priceInput.step = '0.01';
          priceInput.placeholder = 'Seller page';
          var savedPrice = record.items[node.id] && record.items[node.id].actual;
          if (savedPrice != null && savedPrice !== '') priceInput.value = savedPrice;
          priceInput.addEventListener('input', function () {
            var typed = priceInput.value === '' ? null : priceInput.value;
            var next = itemState(node.id);
            if (typed != null) next = 'equipped';
            else if (next !== 'equipped' && next !== 'owned' && next !== 'skipped') next = 'recommended';
            commit(node.id, next || 'recommended', typed);
            paintBudget();
          });
          priceLabel.appendChild(priceInput);
          bill.appendChild(priceLabel);
          col.appendChild(bill);
        }
        return col;
      }

      function walk(node, acc) {
        acc.push(node);
        (node.children || []).forEach(function (child) { walk(child, acc); });
        return acc;
      }

      function onBill(node) {
        var state = itemState(node.id);
        if (state !== 'equipped' && state !== 'owned') return false;
        if (node.offer && node.offer.noteOnly) return false;
        return true;
      }

      function starLine(n) {
        var full = Math.max(0, Math.min(5, n || 0));
        return '★★★★★'.slice(0, full) + '☆☆☆☆☆'.slice(0, 5 - full);
      }

      function itemProfile(node) {
        var model = root.model || {};
        var raid = model.raid || {};
        var floor = node.offer && node.offer.floor != null ? node.offer.floor : (node.offer && node.offer.dollars === 0 ? 0 : null);
        var base = {
          role: 'Lab part',
          blurb: node.line || 'Part of the lab map.',
          stars: {},
          requires: [],
          good: '',
          bad: '',
          example: '',
          floor: floor
        };
        var cards = {
          'RAIDZ2': {
            role: 'Storage defense',
            blurb: 'Protects the pile if two drives fail. It spends two disks on that protection.',
            stars: { Reliability: 5, Capacity: 3, Speed: 3, 'Cost efficiency': 2, 'Beginner friendly': 3 },
            requires: ['4 or more drives', 'A system that can run ZFS, such as TrueNAS or Proxmox with ZFS'],
            good: 'Family photos, the only copy of important files, a NAS you cannot easily rebuild.',
            bad: 'A tiny budget. Two of the disks are protection, not extra space.',
            example: (raid.layouts || []).filter(function (item) { return item.name === 'RAIDZ2'; }).map(function (item) { return 'Usable: ' + item.usable + '. Failures tolerated: ' + item.loss + '.'; })[0] || ''
          },
          'RAIDZ1': {
            role: 'Storage defense',
            blurb: 'Survives one dead drive. The second failure during a rebuild takes the pile.',
            stars: { Reliability: 3, Capacity: 4, Speed: 3, 'Cost efficiency': 4, 'Beginner friendly': 3 },
            requires: ['3 or more drives'],
            good: 'A media shelf you can rebuild from the backup.',
            bad: 'The only copy of files you cannot replace.',
            example: raid.disks >= 3 ? ('About ' + ((raid.disks - 1) * raid.eachTb) + ' TB usable.') : 'Needs at least 3 disks.'
          },
          'Mirror pairs': {
            role: 'Storage defense',
            blurb: 'Every disk has a partner. One partner can die. You get half the raw space.',
            stars: { Reliability: 4, Capacity: 2, Speed: 4, 'Cost efficiency': 3, 'Beginner friendly': 4 },
            requires: ['2 drives to start'],
            good: 'A first serious pile. Easy to picture: one disk is the copy of the other.',
            bad: 'Four disks of movies, where RAIDZ2 keeps more usable space.',
            example: raid.disks ? ('About ' + ((raid.disks * raid.eachTb) / 2) + ' TB usable from ' + (raid.disks * raid.eachTb) + ' TB raw.') : ''
          },
          'No RAID': {
            role: 'Storage defense',
            blurb: 'One disk. Fast to understand. A dead disk takes whatever lived only there.',
            stars: { Reliability: 1, Capacity: 5, Speed: 3, 'Cost efficiency': 5, 'Beginner friendly': 5 },
            requires: ['The backup branch, if the files matter'],
            good: 'A system disk, or a pile you already copy somewhere else.',
            bad: 'The only copy of the photos.',
            example: 'RAID is not a backup. This layout makes that obvious.'
          }
        };
        var card = cards[node.title] || base;
        if (node.title === 'Hard drives' || node.title === 'Drive family') {
          var rows = (model.drives && model.drives.rows) || [];
          card = {
            role: 'Bulk storage',
            blurb: 'The spinning disks that hold the pile. The system stays on an SSD.',
            stars: { Reliability: 4, Capacity: 5, Speed: 2, 'Cost efficiency': 5, 'Beginner friendly': 3 },
            requires: ['CMR', 'A NAS workload rating', 'SATA'],
            good: 'Movies, photos, and backups.',
            bad: 'Booting the operating system. That belongs on an SSD.',
            example: rows.map(function (row) { return row.name + ' — ' + row.result + '.'; }).join(' '),
            candidates: rows
          };
        }
        if (node.title === 'CMR') {
          card = { role: 'Recording method', blurb: 'Conventional recording. A rebuild can write the disk steadily. This is the kind a NAS wants.', stars: { Reliability: 5, Capacity: 4, Speed: 3, 'Cost efficiency': 4, 'Beginner friendly': 4 }, requires: ['A drive whose spec page says CMR'], good: 'RAID, ZFS, and a file server.', bad: 'Nothing, if you can buy it. Prefer it over SMR for the pile.', example: 'IronWolf, Red Plus, Red Pro, and Exos are CMR.' };
        }
        if (node.title === 'SMR') {
          card = { role: 'Recording method', blurb: 'Shingled recording overlaps tracks. It is cheaper per terabyte and hates a RAID rebuild.', stars: { Reliability: 2, Capacity: 5, Speed: 2, 'Cost efficiency': 4, 'Beginner friendly': 2 }, requires: ['Do not use it for the RAID pile'], good: 'A cold disk you write once and rarely rewrite.', bad: 'A mirror or RAIDZ rebuild. Western Digital has said many plain Red 2 TB to 6 TB drives used SMR.', example: 'Plain WD Red in those sizes fails this lab.' };
        }
        if (model.gateway && model.gateway.rows && model.gateway.rows.some(function (row) { return row.name === node.title; })) {
          var grow = model.gateway.rows.filter(function (row) { return row.name === node.title; })[0];
          card = {
            role: 'Network gateway',
            blurb: node.title + ' scored ' + grow.score + ' against this lab. ' + (node.title === model.gateway.ideal ? 'The requirements want this one.' : (node.title === model.gateway.decision ? 'This band can buy this one.' : 'A lower score, or a closed rung.')),
            stars: { Routing: Math.round((grow.score || 0) / 20), VLANs: grow.vlan === 'Pass' ? 5 : 1, 'Ease of use': node.title.indexOf('OPNsense') === 0 ? 2 : 4, Expandability: node.title.indexOf('Dream') !== -1 ? 5 : 3, Value: node.title.indexOf('Omada') !== -1 ? 5 : 3 },
            requires: (model.gateway.requirements || []).map(function (req) { return req.text + ': ' + req.result; }),
            good: 'Score ' + grow.score + ' in this lab. ' + (node.title === model.gateway.decision ? 'This is the pick that fits the band.' : 'It stays in the study.'),
            bad: grow.result === 'Reject' ? 'It fails a requirement for this lab.' : 'A class floor is not the price on the shelf today.',
            example: (model.gateway.rows || []).map(function (row) { return row.name + ' ' + row.score; }).join(' · '),
            floor: floor
          };
        }
        if (!card.floor && floor != null) card.floor = floor;
        if (!card.blurb) card.blurb = base.blurb;
        return card;
      }

      function paintBudget() {
        var old = rootEl.querySelector('.wiz-budget');
        var card = el('aside', 'wiz-budget');
        var settled = settleBuild(root, record);
        var budget = settled.budget;
        var lines = settled.actualBuild.items.map(function (item) {
          var money = item.state === 'owned' ? '$0 owned' : (item.actual != null ? '$' + item.actual + ' typed' : (item.kind === 'planning' ? 'class floor $' + item.planning : (item.kind === 'free' || item.kind === 'design' ? '$0' : 'unpriced')));
          return item.group + ' · ' + item.title + ' ×' + item.quantity + ' · ' + money;
        });
        var head = el('div', 'wiz-cart-head');
        head.appendChild(el('p', 'wiz-level', settled.name));
        card.appendChild(head);
        if (budget.ceiling != null) card.appendChild(el('p', '', 'Budget ceiling $' + budget.ceiling));
        card.appendChild(el('p', 'wiz-cart-total', 'Known selected cost $' + budget.known));
        var nameLabel = el('label', 'wiz-price', 'Build name');
        var nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = record.name || settled.name;
        nameInput.addEventListener('change', function () {
          record.name = nameInput.value;
          persist();
          paintBudget();
        });
        nameLabel.appendChild(nameInput);
        card.appendChild(nameLabel);
        var truth = el('p', budget.status === 'incomplete' ? 'is-incomplete' : '', budget.line);
        card.appendChild(truth);
        card.appendChild(el('p', '', 'Unpriced selected items: ' + budget.unpriced));
        if (budget.estimated != null) card.appendChild(el('p', '', 'Estimated complete build ~$' + budget.estimated + '. Not charged until you equip a part.'));
        var ready = settled.readiness;
        var pricingLabel = { incomplete: 'INCOMPLETE', priced: 'PRICED', over: 'OVER BUDGET' }[budget.status] || budget.status;
        card.appendChild(el('p', '', 'PRICING STATUS: ' + pricingLabel));
        card.appendChild(el('p', '', 'BUILD READINESS: ' + ready.percent + '%'));
        var readyRow = el('div', 'wiz-stat');
        readyRow.appendChild(el('span', '', 'Readiness'));
        var track = el('span', 'wiz-bar');
        var fill = document.createElement('i');
        fill.style.width = ready.percent + '%';
        track.appendChild(fill);
        readyRow.appendChild(track);
        readyRow.appendChild(el('span', '', ready.percent + '%'));
        card.appendChild(readyRow);
        if (budget.status === 'over') card.appendChild(el('p', 'wiz-cart-over', '⚠ $' + (budget.known - budget.ceiling) + ' over the band'));
        Object.keys(settled.groups).forEach(function (group) {
          var row = el('div', 'wiz-cart-row');
          row.appendChild(el('span', '', group));
          var bucket = settled.groups[group];
          var groupText = bucket.unpriced ? ('$' + bucket.known + ' + ' + bucket.unpriced + ' unpriced') : ('$' + bucket.known);
          row.appendChild(el('span', '', groupText));
          card.appendChild(row);
        });
        var count = settled.actualBuild.items.length;
        card.appendChild(el('p', 'wiz-cart-count', count + (count === 1 ? ' item equipped or owned' : ' items equipped or owned')));
        var view = document.createElement('button');
        view.type = 'button';
        view.className = 'wiz-chip';
        view.textContent = cartOpen ? 'Hide the build' : 'View the build';
        view.addEventListener('mousedown', function (event) { event.preventDefault(); });
        view.addEventListener('click', function () {
          cartOpen = !cartOpen;
          paintBudget();
        });
        card.appendChild(view);
        if (cartOpen) {
          var more = el('div', 'wiz-cart-more');
          lines.forEach(function (line) { more.appendChild(el('p', '', line)); });
          if (root.model && root.model.conflict) {
            more.appendChild(el('h3', '', 'Budget conflict'));
            root.model.conflict.lines.forEach(function (line) { more.appendChild(el('p', '', line)); });
          }
          if (root.model && root.model.forecast) {
            more.appendChild(el('h3', '', 'If you spend more'));
            root.model.forecast.forEach(function (rung) { more.appendChild(el('p', '', rung.line)); });
          }
          if (ready.missing.length) {
            more.appendChild(el('h3', '', 'Open required slots'));
            more.appendChild(el('p', '', ready.missing.join(', ')));
          }
          if (ready.unresolved.length) {
            more.appendChild(el('h3', '', 'Unresolved'));
            ready.unresolved.forEach(function (line) { more.appendChild(el('p', '', line)); });
          }
          more.appendChild(el('p', '', 'A class floor is budget math, dated Sep 24, 2026. It does not change when a store changes its price. Type the price you saw to replace it.'));
          card.appendChild(more);
        }
        var tools = el('div', 'wiz-actions');
        function tool(label, run) {
          var button = document.createElement('button');
          button.type = 'button';
          button.className = 'wiz-chip';
          button.textContent = label;
          button.addEventListener('mousedown', function (event) { event.preventDefault(); });
          button.addEventListener('click', run);
          tools.appendChild(button);
        }
        tool('Save', function () { persist(); });
        tool('Load', function () { restore(); paint(); });
        tool('Reset', function () {
          record.name = '';
          record.items = {};
          try { localStorage.removeItem(STORAGE_KEY); } catch (err) { /* ignore */ }
          paint();
        });
        tool('Export', function () {
          var blob = new Blob([JSON.stringify({ version: 1, answers: answers, name: record.name, items: record.items, switchPlan: record.switchPlan || null }, null, 2)], { type: 'application/json' });
          var url = URL.createObjectURL(blob);
          var link = document.createElement('a');
          link.href = url;
          link.download = 'lab-build.json';
          link.click();
          URL.revokeObjectURL(url);
        });
        var file = document.createElement('input');
        file.type = 'file';
        file.accept = 'application/json';
        file.hidden = true;
        file.addEventListener('change', function () {
          var picked = file.files && file.files[0];
          if (!picked) return;
          var reader = new FileReader();
          reader.onload = function () {
            var data = null;
            try { data = JSON.parse(String(reader.result || '')); } catch (err) { data = null; }
            var reason = acceptImport(data);
            if (reason) {
              window.alert(reason);
              return;
            }
            Object.keys(answers).forEach(function (key) { delete answers[key]; });
            Object.keys(data.answers).forEach(function (key) { answers[key] = data.answers[key]; });
            record.name = data.name || '';
            record.items = data.items;
            record.switchPlan = data.switchPlan || null;
            persist();
            index = 999;
            draw();
          };
          reader.readAsText(picked);
        });
        tool('Import', function () { file.click(); });
        card.appendChild(file);
        card.appendChild(tools);
        if (old) rootEl.replaceChild(card, old);
        else {
          var layout = rootEl.querySelector('.wiz-layout');
          if (layout) rootEl.insertBefore(card, layout);
          else rootEl.insertBefore(card, rootEl.firstChild);
        }
      }

      function switchSizer() {
        var box = el('div', '');
        box.appendChild(el('h3', '', 'Size your switch'));
        var saved = record.switchPlan || {};
        function field(label, key) {
          var wrap = el('label', 'wiz-price', label);
          var input = document.createElement('input');
          input.type = 'number';
          input.min = '0';
          input.step = '1';
          input.value = saved[key] != null ? saved[key] : 0;
          wrap.appendChild(input);
          box.appendChild(wrap);
          return input;
        }
        var wired = field('Wired devices', 'wired');
        var cameras = field('PoE cameras', 'cameras');
        var aps = field('Wi-Fi access points', 'aps');
        var otherPoe = field('Other PoE devices', 'otherPoe');
        var calc = document.createElement('button');
        calc.type = 'button';
        calc.className = 'wiz-chip';
        calc.textContent = 'Calculate';
        calc.addEventListener('mousedown', function (event) { event.preventDefault(); });
        calc.addEventListener('click', function () {
          record.switchPlan = sizeSwitch({
            wired: Number(wired.value),
            cameras: Number(cameras.value),
            aps: Number(aps.value),
            otherPoe: Number(otherPoe.value),
            speed: '1',
            uplink10: false
          });
          persist();
          paint();
        });
        box.appendChild(calc);
        if (saved.minimumPorts != null) {
          box.appendChild(el('p', '', 'Minimum physical ports ' + saved.minimumPorts + '. Recommended ' + saved.recommendedPorts + '.'));
          box.appendChild(el('p', '', 'PoE ports ' + saved.poePorts + '. Minimum PoE budget ' + saved.poeWatts + ' W. Recommended reserve ' + saved.poeReserveWatts + ' W.'));
          box.appendChild(el('p', '', 'VLANs ' + (saved.vlans ? 'required' : 'not required from this count') + '.'));
        }
        return box;
      }

      function renderItem(node) {
        var card = itemProfile(node);
        var box = el('aside', 'wiz-drawer wiz-item');
        var close = document.createElement('button');
        close.type = 'button';
        close.className = 'btn btn-ghost wiz-back';
        close.textContent = 'Close';
        close.addEventListener('mousedown', function (event) { event.preventDefault(); });
        close.addEventListener('click', function () { inspected = null; paint(); });
        box.appendChild(close);
        if (node.product) box.appendChild(renderProductGear(node));
        else box.appendChild(el('p', 'wiz-level', card.role));
        box.appendChild(el('h2', 'wiz-title', node.title));
        var cpuPart = (PARTS.cpu || []).filter(function (part) { return part.name === node.title; })[0];
        if (cpuPart && cpuPart.arch) {
          box.appendChild(el('p', 'wiz-badge', cpuPart.arch + ' · ' + cpuPart.socket + ' · ' + cpuPart.cores + ' cores / ' + cpuPart.threads + ' threads · ' + cpuPart.watts + ' W · ' + cpuPart.memory + (cpuPart.igpu ? ' · integrated graphics' : '')));
          box.appendChild(el('p', '', 'Architecture is the generation of the chip. Zen 4 is newer than Zen 3. A newer architecture can do more work per watt. It does not, by itself, decide how large an AI model fits in video memory. That is the graphics card.'));
        }
        box.appendChild(el('p', '', card.blurb));
        Object.keys(card.stars || {}).forEach(function (name) {
          var row = el('div', 'wiz-stat');
          row.appendChild(el('span', '', name));
          row.appendChild(el('span', '', starLine(card.stars[name])));
          box.appendChild(row);
        });
        if (card.requires && card.requires.length) {
          box.appendChild(el('h3', '', 'Requires'));
          card.requires.forEach(function (line) { box.appendChild(el('p', '', line)); });
        }
        if (card.example) box.appendChild(el('p', '', card.example));
        if (card.good) box.appendChild(el('p', '', 'Good for: ' + card.good));
        if (card.bad) box.appendChild(el('p', '', 'Bad for: ' + card.bad));
        if (card.candidates && card.candidates.length) {
          box.appendChild(el('h3', '', 'Candidates'));
          card.candidates.forEach(function (row) { box.appendChild(el('p', '', row.name + ' — ' + row.result)); });
        }
        var price = card.floor == null ? 'No class floor on this choice. The shelf price stays on the seller page.' : ('Class floor $' + card.floor + ', dated Sep 24, 2026. Amazon, Newegg, and B&H are not filled in here.');
        box.appendChild(el('p', '', price));
        box.appendChild(renderMarkets(node.product ? node.product.model : node.title));
        var actions = el('div', 'wiz-actions');
        var verbs = {
          hardware: { take: 'Equip', taken: 'Equipped', own: 'I already own this', owned: 'Owned' },
          optional: { take: 'Equip', taken: 'Equipped', own: 'I already own this', owned: 'Owned' },
          architecture: { take: 'Select', taken: 'Selected' },
          'free-software': { take: 'Install', taken: 'In use' },
          'paid-software': { take: 'Add license', taken: 'Licensed' }
        }[node.kind] || { take: 'Equip', taken: 'Equipped', own: 'I already own this', owned: 'Owned' };
        var add = document.createElement('button');
        add.type = 'button';
        add.className = 'wiz-chip';
        var equippedNow = itemState(node.id) === 'equipped';
        add.textContent = equippedNow ? verbs.taken : (verbs.take + (node.kind === 'hardware' && card.floor ? (' — class floor $' + card.floor) : ''));
        add.addEventListener('mousedown', function (event) { event.preventDefault(); });
        add.addEventListener('click', function () {
          commit(node.id, 'equipped');
          paint();
        });
        actions.appendChild(add);
        if (node.product) {
          var upgrade = document.createElement('button');
          upgrade.type = 'button';
          upgrade.className = 'wiz-chip';
          upgrade.textContent = 'Upgrade';
          upgrade.addEventListener('mousedown', function (event) { event.preventDefault(); });
          upgrade.addEventListener('click', function () {
            record.upgradeFrom = node.product.id;
            paint();
          });
          actions.appendChild(upgrade);
          var compare = document.createElement('button');
          compare.type = 'button';
          compare.className = 'wiz-chip';
          compare.textContent = 'Compare';
          compare.addEventListener('mousedown', function (event) { event.preventDefault(); });
          compare.addEventListener('click', function () {
            record.compare = record.compare || [];
            if (record.compare.indexOf(node.product.id) === -1 && record.compare.length < 3) record.compare.push(node.product.id);
            paint();
          });
          actions.appendChild(compare);
        }
        if (verbs.own) {
          var own = document.createElement('button');
          own.type = 'button';
          own.className = 'wiz-chip';
          own.textContent = itemState(node.id) === 'owned' ? verbs.owned : verbs.own;
          own.addEventListener('mousedown', function (event) { event.preventDefault(); });
          own.addEventListener('click', function () {
            commit(node.id, 'owned', null);
            paint();
          });
          actions.appendChild(own);
        }
        if (node.offer && node.offer.qty > 1) {
          var qtyLabel = el('label', 'wiz-price', 'Quantity');
          var qtyInput = document.createElement('input');
          qtyInput.type = 'number';
          qtyInput.min = '1';
          qtyInput.step = '1';
          qtyInput.value = (record.items[node.id] && record.items[node.id].quantity) || node.offer.qty;
          qtyInput.addEventListener('change', function () {
            var nextQty = Math.max(1, Number(qtyInput.value) || node.offer.qty);
            commit(node.id, itemState(node.id) || 'equipped', undefined, nextQty);
            paint();
          });
          qtyLabel.appendChild(qtyInput);
          actions.appendChild(qtyLabel);
        }
        box.appendChild(actions);
        if (node.id && node.id.indexOf('sw-') === 0) box.appendChild(switchSizer());
        if (node.product && record.upgradeFrom === node.product.id) box.appendChild(renderUpgrade(node.product));
        if (record.compare && record.compare.length) box.appendChild(renderCompare());
        return box;
      }

      function renderProductGear(node) {
        var product = node.product;
        var scores = gpuScores(product);
        var head = el('div', 'wiz-gear');
        head.appendChild(el('p', 'wiz-badge', product.vendor + ' · ' + product.architecture));
        head.appendChild(el('p', 'wiz-gear-kicker', product.generation + ' · ' + product.vram_gb + ' GB ' + product.memory));
        var plate = el('div', 'wiz-plate');
        plate.appendChild(el('strong', '', product.architecture.slice(0, 3).toUpperCase()));
        plate.appendChild(el('span', '', product.watts + ' W'));
        head.appendChild(plate);
        ['ai', 'gaming', 'efficiency'].forEach(function (name) {
          var row = el('div', 'wiz-stat');
          row.appendChild(el('span', '', name === 'ai' ? 'AI' : (name === 'gaming' ? 'Gaming' : 'Efficiency')));
          var track = el('span', 'wiz-bar');
          var fill = document.createElement('i');
          fill.style.width = scores[name] + '%';
          track.appendChild(fill);
          row.appendChild(track);
          row.appendChild(el('span', '', String(scores[name])));
          head.appendChild(row);
        });
        head.appendChild(el('p', 'wiz-note', 'These bars come from VRAM, generation, and watts. They are not a benchmark.'));
        head.appendChild(el('p', '', 'Encoder: ' + product.encoder + '. Vendor system power: ' + product.psu + ' W.'));
        var current = equippedGpu();
        if (current && current.id !== product.id) {
          var cpuWatts = root.model && root.model.fit && root.model.fit.cpu ? root.model.fit.cpu.watts : 0;
          var psuWatts = root.model && root.model.fit && root.model.fit.psu ? root.model.fit.psu.watts : null;
          var impact = gpuSwapImpact(current, product, cpuWatts, psuWatts);
          head.appendChild(el('h3', '', 'Build impact'));
          head.appendChild(el('p', '', 'VRAM ' + impact.vram[0] + ' GB → ' + impact.vram[1] + ' GB'));
          head.appendChild(el('p', '', 'Power ' + impact.watts[0] + ' W → ' + impact.watts[1] + ' W'));
          head.appendChild(el('p', '', 'This checker wants about ' + impact.formulaNeed + ' W before headroom.' + (impact.formulaOk === false ? ' The suggested power supply is short of that.' : '')));
          if (impact.vendorOk === false) head.appendChild(el('p', 'wiz-cart-over', product.vendor + ' lists a ' + product.psu + ' W system power supply for this card.'));
        }
        return head;
      }

      function equippedGpu() {
        var ids = Object.keys(record.items || {});
        for (var i = 0; i < ids.length; i++) {
          var state = record.items[ids[i]] && record.items[ids[i]].state;
          if (state !== 'equipped' && state !== 'owned') continue;
          var found = GPU_CATALOG.filter(function (item) { return ids[i] === 'gpu-' + item.id; })[0];
          if (found) return found;
        }
        return null;
      }

      function renderUpgrade(product) {
        var box = el('div', 'wiz-upgrade');
        box.appendChild(el('h3', '', 'Upgrade from ' + product.model));
        box.appendChild(el('p', '', 'Price deltas stay unknown until an offer has a checked price. Power and VRAM still change.'));
        upgradePaths(product.id).forEach(function (row) {
          var impact = gpuSwapImpact(product, row.product, 0, null);
          var line = el('p', '');
          line.appendChild(el('strong', '', row.role + ' · ' + row.product.model));
          line.appendChild(document.createTextNode(' ' + row.product.architecture + ' · ' + impact.vram[0] + ' GB → ' + impact.vram[1] + ' GB · ' + impact.watts[0] + ' W → ' + impact.watts[1] + ' W'));
          box.appendChild(line);
        });
        return box;
      }

      function renderCompare() {
        var box = el('div', 'wiz-compare');
        box.appendChild(el('h3', '', 'Compare'));
        var row = el('div', 'wiz-compare-row');
        var picked = (record.compare || []).map(function (id) {
          return GPU_CATALOG.filter(function (item) { return item.id === id; })[0];
        }).filter(Boolean);
        var best = picked.slice().sort(function (a, b) { return gpuScores(b).ai - gpuScores(a).ai; })[0];
        picked.forEach(function (product) {
          var scores = gpuScores(product);
          var card = el('article', 'wiz-gear-card');
          card.appendChild(el('strong', '', product.model));
          card.appendChild(el('p', '', product.architecture + ' · ' + product.vram_gb + ' GB'));
          card.appendChild(el('p', '', 'AI ' + scores.ai + ' · Gaming ' + scores.gaming + ' · Power ' + scores.efficiency));
          card.appendChild(el('p', '', 'Price not checked'));
          row.appendChild(card);
        });
        box.appendChild(row);
        if (best) box.appendChild(el('p', '', 'Highest AI score in this comparison: ' + best.model + '. A newer architecture does not replace VRAM.'));
        var tech = document.createElement('details');
        var summary = document.createElement('summary');
        summary.textContent = 'Technical trade study';
        tech.appendChild(summary);
        picked.forEach(function (product) {
          tech.appendChild(el('p', '', product.model + ' · ' + product.architecture + ' · ' + product.vram_gb + ' GB ' + product.memory + ' · ' + product.watts + ' W · ' + product.encoder + ' · vendor PSU ' + product.psu + ' W'));
        });
        box.appendChild(tech);
        var clear = document.createElement('button');
        clear.type = 'button';
        clear.className = 'wiz-chip';
        clear.textContent = 'Clear compare';
        clear.addEventListener('click', function () { record.compare = []; paint(); });
        box.appendChild(clear);
        return box;
      }

      function renderMarkets(query) {
        var wrap = el('div', 'wiz-markets');
        wrap.appendChild(el('h3', '', 'Offers'));
        record.offerFilter = record.offerFilter || 'all';
        var filters = el('div', 'wiz-actions');
        [['all', 'Used okay'], ['new', 'New only'], ['cheapest', 'Cheapest'], ['warranty', 'Best warranty']].forEach(function (pair) {
          var button = document.createElement('button');
          button.type = 'button';
          button.className = 'wiz-chip' + (record.offerFilter === pair[0] ? ' is-on' : '');
          button.textContent = pair[1];
          button.addEventListener('mousedown', function (event) { event.preventDefault(); });
          button.addEventListener('click', function () { record.offerFilter = pair[0]; paint(); });
          filters.appendChild(button);
        });
        wrap.appendChild(filters);
        var offers = marketOffers(query);
        if (record.offerFilter === 'cheapest') wrap.appendChild(el('p', '', 'No checked price, so the cheapest seller is unknown.'));
        else if (record.offerFilter === 'warranty') wrap.appendChild(el('p', '', 'Warranty is not on these offers yet. Read it on the seller page.'));
        offers.filter(function (offer) {
          if (record.offerFilter === 'new') return offer.condition === 'new';
          return true;
        }).forEach(function (offer) {
          var line = el('p', 'wiz-offer');
          line.appendChild(el('span', '', offer.condition === 'new' ? 'New' : 'Used'));
          var link = document.createElement('a');
          link.href = offer.url;
          link.target = '_blank';
          link.rel = 'noopener';
          link.textContent = offer.market;
          line.appendChild(link);
          line.appendChild(el('span', '', 'Not checked'));
          wrap.appendChild(line);
        });
        return wrap;
      }

      function restoreScroll(x, y) {
        var html = document.documentElement;
        var prev = html.style.scrollBehavior;
        html.style.scrollBehavior = 'auto';
        window.scrollTo(x, y);
        html.style.scrollBehavior = prev;
      }

      function paint() {
        var scrollX = window.scrollX;
        var scrollY = window.scrollY;
        rootEl.style.minHeight = rootEl.offsetHeight + 'px';
        rootEl.innerHTML = '';
        var layout = el('div', 'wiz-layout');
        var stage = el('div', 'wiz-stage');
        stage.appendChild(renderCol(root, [root.id]));
        layout.appendChild(stage);
        if (inspected) layout.appendChild(renderItem(inspected));
        else if (focus) layout.appendChild(renderDrawer(focus));
        rootEl.appendChild(layout);
        if (openIds.length > 1) {
          var up = document.createElement('button');
          up.type = 'button';
          up.className = 'btn btn-ghost wiz-back';
          up.textContent = 'Back';
          up.addEventListener('mousedown', function (event) { event.preventDefault(); });
          up.addEventListener('click', function () {
            focus = null;
            openIds = openIds.slice(0, -1);
            paint();
          });
          rootEl.appendChild(up);
        }
        var again = document.createElement('button');
        again.type = 'button';
        again.className = 'btn btn-primary wiz-back';
        again.textContent = 'Start over';
        again.addEventListener('click', function () {
          answers = {};
          index = 0;
          record = { version: 1, name: '', items: {} };
          try { localStorage.removeItem(STORAGE_KEY); } catch (err) { /* ignore */ }
          draw();
        });
        rootEl.appendChild(again);
        paintBudget();
        restoreScroll(scrollX, scrollY);
        var tip = rootEl.querySelector('.is-tip');
        var nudged = false;
        if (tip) {
          var rect = tip.getBoundingClientRect();
          var off = rect.bottom < 0 || rect.top > window.innerHeight;
          if (off) {
            nudged = true;
            tip.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
          }
        }
        rootEl.style.minHeight = '';
        if (!nudged) requestAnimationFrame(function () { restoreScroll(scrollX, scrollY); });
      }
      paint();
    }

    function section(title, paragraphs) {
      var box = el('section', 'wiz-block');
      box.appendChild(el('h3', '', title));
      paragraphs.forEach(function (text) {
        if (text) box.appendChild(el('p', '', text));
      });
      return box;
    }

    function listSection(title, items) {
      var box = el('section', 'wiz-block');
      box.appendChild(el('h3', '', title));
      var ul = document.createElement('ul');
      items.forEach(function (item) {
        ul.appendChild(el('li', '', item));
      });
      box.appendChild(ul);
      return box;
    }

    function lessonSection(item) {
      var box = el('section', 'wiz-block');
      box.appendChild(el('h3', '', item.title));
      (item.paragraphs || []).forEach(function (text) {
        if (text) box.appendChild(el('p', '', text));
      });
      if (item.steps && item.steps.length) {
        var ol = document.createElement('ol');
        item.steps.forEach(function (step) {
          ol.appendChild(el('li', '', step));
        });
        box.appendChild(ol);
      }
      if (item.links && item.links.length) {
        var ul = document.createElement('ul');
        item.links.forEach(function (link) {
          var li = document.createElement('li');
          var anchor = document.createElement('a');
          anchor.href = link.href;
          anchor.textContent = link.name;
          if (String(link.href).indexOf('http') === 0) {
            anchor.target = '_blank';
            anchor.rel = 'noopener';
          }
          li.appendChild(anchor);
          if (link.detail) li.appendChild(document.createTextNode('. ' + link.detail));
          ul.appendChild(li);
        });
        box.appendChild(ul);
      }
      return box;
    }

    function linkSection(title, items) {
      var box = el('section', 'wiz-block');
      box.appendChild(el('h3', '', title));
      var ul = document.createElement('ul');
      items.forEach(function (item) {
        var li = document.createElement('li');
        var link = document.createElement('a');
        link.href = item.href;
        link.textContent = item.name;
        if (item.href.indexOf('http') === 0) {
          link.target = '_blank';
          link.rel = 'noopener';
        }
        li.appendChild(link);
        li.appendChild(document.createTextNode('. ' + item.detail));
        ul.appendChild(li);
      });
      box.appendChild(ul);
      return box;
    }

    draw();
  }

  function leaf(id, level, title, line, sections) {
    return { id: id, level: level, title: title, line: line || '', children: [], sections: sections || [] };
  }

  function branch(id, level, title, children) {
    return { id: id, level: level, title: title, line: '', children: children || [], sections: [] };
  }

  function note(name, lines, slot) {
    return { name: name, slot: slot || 'why', lines: (lines || []).filter(function (line) { return line; }) };
  }

  function asSlot(item, slot) {
    if (item) item.slot = slot;
    return item;
  }

  function tag(node, kind, offer, status) {
    node.kind = kind;
    if (offer) node.offer = offer;
    if (status) node.status = status;
    if (status === 'ready' || status === 'selected' || status === 'over') node.selected = true;
    return node;
  }

  function lessonNote(report, key, name) {
    var found = (report.plan.advanced || []).filter(function (item) {
      return String(item.title || '').toLowerCase().indexOf(key) !== -1;
    })[0];
    if (!found) return null;
    var lines = (found.paragraphs || []).concat(found.steps || []).concat(found.links || []);
    return note(name, lines);
  }

  function osLeaf(report, level) {
    var plan = report.plan;
    var card = leaf('os', level || 'L5', report.pick === 'proxmox' ? 'Proxmox VE' : report.profile.name, report.pick === 'proxmox'
      ? 'Runs the virtual computers in your lab.'
      : report.profile.plain, [
      note('Why we picked it', [report.because, report.labLine], 'why'),
      note('How it fits your lab', [report.jobs.length ? 'This lab is for ' + report.jobs.join(', ') + '.' : ''], 'compare'),
      note('How to install it', (plan.setup || []).concat(plan.path || []), 'install'),
      note('Requirements', [report.hardware.ram, report.hardware.gpuLabel, report.hardware.storage], 'requirements')
    ]);
    return tag(card, 'free-software', { group: 'Software', name: card.title, dollars: 0 }, 'ready');
  }

  var HDD_8TB = [
    { id: 'st8000vn004', brand: 'Seagate', model: 'IronWolf 8TB', mpn: 'ST8000VN004', category: 'hdd', capacity_tb: 8, recording: 'CMR', interface: 'SATA', rpm: 7200, warranty_years: 3, workload: 'NAS', noise: 'home', price_per_unit: null },
    { id: 'wd80efpx', brand: 'WD', model: 'Red Plus 8TB', mpn: 'WD80EFPX', category: 'hdd', capacity_tb: 8, recording: 'CMR', interface: 'SATA', rpm: 5640, warranty_years: 3, workload: 'NAS', noise: 'home', price_per_unit: null },
    { id: 'wd8003ffbx', brand: 'WD', model: 'Red Pro 8TB', mpn: 'WD8003FFBX', category: 'hdd', capacity_tb: 8, recording: 'CMR', interface: 'SATA', rpm: 7200, warranty_years: 5, workload: 'NAS', noise: 'home', price_per_unit: null },
    { id: 'st8000nm000a', brand: 'Seagate', model: 'Exos 8TB', mpn: 'ST8000NM000A', category: 'hdd', capacity_tb: 8, recording: 'CMR', interface: 'SATA', rpm: 7200, warranty_years: 5, workload: 'enterprise', noise: 'loud', price_per_unit: null },
    { id: 'wd84purz', brand: 'WD', model: 'Purple 8TB', mpn: 'WD84PURZ', category: 'hdd', capacity_tb: 8, recording: 'CMR', interface: 'SATA', rpm: 5640, warranty_years: 3, workload: 'surveillance', noise: 'home', price_per_unit: null },
    { id: 'wd-black-8tb', brand: 'WD', model: 'Black 8TB', mpn: null, category: 'hdd', capacity_tb: 8, recording: 'CMR', interface: 'SATA', rpm: 7200, warranty_years: 5, workload: 'desktop', noise: 'home', price_per_unit: null }
  ];

  function hddScores(drive) {
    return {
      warranty: drive.warranty_years >= 5 ? 100 : 60,
      noise: drive.noise === 'loud' ? 35 : (drive.rpm <= 5700 ? 90 : 70),
      performance: drive.rpm >= 7200 ? 80 : 55,
      reliability: drive.workload === 'enterprise' ? 85 : (drive.workload === 'NAS' ? 80 : 40),
      price: drive.price_per_unit
    };
  }

  function scoreTrade(candidates, spec) {
    var weights = (spec && spec.weights) || {};
    var keys = Object.keys(weights).filter(function (key) {
      return (candidates || []).some(function (row) { return row.scores && row.scores[key] != null; });
    });
    var sum = 0;
    keys.forEach(function (key) { sum += Number(weights[key]) || 0; });
    var rows = (candidates || []).map(function (row) {
      var failed = ((spec && spec.mandatory) || []).filter(function (rule) { return !rule.pass(row); });
      if (failed.length) return { id: row.id, name: row.model || row.name, result: 'Reject', score: 0, why: failed[0].text };
      var score = 0;
      if (sum) keys.forEach(function (key) { score += (row.scores[key] || 0) * weights[key]; });
      return { id: row.id, name: row.model || row.name, result: 'Qualifies', score: sum ? Math.round(score / sum) : 0, why: '' };
    });
    var ranked = rows.filter(function (row) { return row.result === 'Qualifies'; }).sort(function (a, b) {
      return b.score - a.score || String(a.name).localeCompare(String(b.name));
    });
    return { rows: rows, winner: ranked[0] || null, weightsUsed: keys };
  }

  function sizeSwitch(input) {
    var src = input || {};
    var wired = Math.max(0, Number(src.wired) || 0);
    var cameras = Math.max(0, Number(src.cameras) || 0);
    var aps = Math.max(0, Number(src.aps) || 0);
    var other = Math.max(0, Number(src.otherPoe) || 0);
    var minimumPorts = wired + cameras + aps + other + 2;
    var sizes = [8, 16, 24, 48];
    var recommendedPorts = sizes.filter(function (size) { return size >= minimumPorts; })[0] || minimumPorts;
    var poePorts = cameras + aps + other;
    var poeWatts = Math.round(poePorts * 15.4 * 10) / 10;
    return {
      wired: wired,
      cameras: cameras,
      aps: aps,
      otherPoe: other,
      speed: src.speed || '1',
      uplink10: !!src.uplink10,
      minimumPorts: minimumPorts,
      recommendedPorts: recommendedPorts,
      poePorts: poePorts,
      poeWatts: poeWatts,
      poeReserveWatts: Math.ceil(poeWatts * 1.25),
      vlans: cameras > 0 || aps > 0
    };
  }

  function acceptImport(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) return 'This file is not a lab build.';
    if (data.version !== 1) return 'This file is not a version 1 lab build.';
    if (!data.answers || typeof data.answers !== 'object' || Array.isArray(data.answers)) return 'This file has no saved answers.';
    if (!data.items || typeof data.items !== 'object' || Array.isArray(data.items)) return 'This file has no saved items.';
    var states = { recommended: 1, equipped: 1, owned: 1, skipped: 1 };
    var ids = Object.keys(data.items);
    for (var i = 0; i < ids.length; i++) {
      var item = data.items[ids[i]];
      if (!item || !states[item.state]) return 'An item has a state this version does not know.';
      if (item.quantity != null && (!isFinite(Number(item.quantity)) || Number(item.quantity) < 1)) return 'An item has a bad quantity.';
    }
    return '';
  }

  var MARKETS = [
    { id: 'amazon', name: 'Amazon', condition: 'new', search: 'https://www.amazon.com/s?k=' },
    { id: 'newegg', name: 'Newegg', condition: 'new', search: 'https://www.newegg.com/p/pl?d=' },
    { id: 'bh', name: 'B&H', condition: 'new', search: 'https://www.bhphotovideo.com/c/search?q=' },
    { id: 'bestbuy', name: 'Best Buy', condition: 'new', search: 'https://www.bestbuy.com/site/searchpage.jsp?st=' },
    { id: 'pcpartpicker', name: 'PCPartPicker', condition: 'new', search: 'https://pcpartpicker.com/search/?q=' },
    { id: 'jawa', name: 'Jawa', condition: 'used', search: 'https://www.jawa.gg/search?query=' },
    { id: 'ebay', name: 'eBay', condition: 'used', search: 'https://www.ebay.com/sch/i.html?_nkw=' }
  ];

  var GPU_CATALOG = [
    { id: 'rtx-3060-12', vendor: 'NVIDIA', model: 'RTX 3060 12GB', architecture: 'Ampere', generation: 'RTX 30', vram_gb: 12, memory: 'GDDR6', watts: 170, psu: 550, encoder: 'NVENC 7th gen', length_mm: null },
    { id: 'rtx-3080-10', vendor: 'NVIDIA', model: 'RTX 3080 10GB', architecture: 'Ampere', generation: 'RTX 30', vram_gb: 10, memory: 'GDDR6X', watts: 320, psu: 750, encoder: 'NVENC 7th gen', length_mm: null },
    { id: 'rtx-3090-24', vendor: 'NVIDIA', model: 'RTX 3090 24GB', architecture: 'Ampere', generation: 'RTX 30', vram_gb: 24, memory: 'GDDR6X', watts: 350, psu: 750, encoder: 'NVENC 7th gen', length_mm: null },
    { id: 'rtx-4060-8', vendor: 'NVIDIA', model: 'RTX 4060 8GB', architecture: 'Ada Lovelace', generation: 'RTX 40', vram_gb: 8, memory: 'GDDR6', watts: 115, psu: 550, encoder: 'NVENC 8th gen', length_mm: null },
    { id: 'rtx-4070-12', vendor: 'NVIDIA', model: 'RTX 4070 12GB', architecture: 'Ada Lovelace', generation: 'RTX 40', vram_gb: 12, memory: 'GDDR6X', watts: 200, psu: 650, encoder: 'NVENC 8th gen', length_mm: null },
    { id: 'rtx-4090-24', vendor: 'NVIDIA', model: 'RTX 4090 24GB', architecture: 'Ada Lovelace', generation: 'RTX 40', vram_gb: 24, memory: 'GDDR6X', watts: 450, psu: 850, encoder: 'NVENC 8th gen', length_mm: null },
    { id: 'rtx-5070-12', vendor: 'NVIDIA', model: 'RTX 5070 12GB', architecture: 'Blackwell', generation: 'RTX 50', vram_gb: 12, memory: 'GDDR7', watts: 250, psu: 650, encoder: 'NVENC 9th gen', length_mm: null },
    { id: 'rtx-5070ti-16', vendor: 'NVIDIA', model: 'RTX 5070 Ti 16GB', architecture: 'Blackwell', generation: 'RTX 50', vram_gb: 16, memory: 'GDDR7', watts: 300, psu: 750, encoder: 'NVENC 9th gen', length_mm: null },
    { id: 'rtx-5080-16', vendor: 'NVIDIA', model: 'RTX 5080 16GB', architecture: 'Blackwell', generation: 'RTX 50', vram_gb: 16, memory: 'GDDR7', watts: 360, psu: 850, encoder: 'NVENC 9th gen', length_mm: 304 },
    { id: 'rx-6700xt-12', vendor: 'AMD', model: 'RX 6700 XT 12GB', architecture: 'RDNA 2', generation: 'RX 6000', vram_gb: 12, memory: 'GDDR6', watts: 230, psu: 650, encoder: 'AMF', length_mm: null },
    { id: 'rx-7800xt-16', vendor: 'AMD', model: 'RX 7800 XT 16GB', architecture: 'RDNA 3', generation: 'RX 7000', vram_gb: 16, memory: 'GDDR6', watts: 263, psu: 700, encoder: 'AMF', length_mm: null },
    { id: 'rx-7900xtx-24', vendor: 'AMD', model: 'RX 7900 XTX 24GB', architecture: 'RDNA 3', generation: 'RX 7000', vram_gb: 24, memory: 'GDDR6', watts: 355, psu: 800, encoder: 'AMF', length_mm: null },
    { id: 'arc-a770-16', vendor: 'Intel', model: 'Arc A770 16GB', architecture: 'Alchemist', generation: 'Arc A', vram_gb: 16, memory: 'GDDR6', watts: 225, psu: 600, encoder: 'Arc AV1', length_mm: null },
    { id: 'arc-b580-12', vendor: 'Intel', model: 'Arc B580 12GB', architecture: 'Battlemage', generation: 'Arc B', vram_gb: 12, memory: 'GDDR6', watts: 190, psu: 600, encoder: 'Arc AV1', length_mm: null }
  ];

  var GPU_GENERATION = { 'Ampere': 3, 'Ada Lovelace': 4, 'Blackwell': 5, 'RDNA 2': 3, 'RDNA 3': 4, 'Alchemist': 3, 'Battlemage': 4 };

  function gpuScores(product) {
    var gen = GPU_GENERATION[product.architecture] || 0;
    return {
      ai: Math.min(99, product.vram_gb * 3 + gen * 2),
      gaming: Math.min(99, gen * 16 + Math.min(product.vram_gb, 16)),
      efficiency: Math.max(20, Math.min(95, 110 - Math.round(product.watts / 5)))
    };
  }

  function marketOffers(query) {
    return MARKETS.map(function (market) {
      return {
        market: market.name,
        condition: market.condition,
        price: null,
        shipping: null,
        returns: null,
        warranty: null,
        sellerRating: null,
        stock: null,
        checked_at: null,
        url: market.search + encodeURIComponent(query || '')
      };
    });
  }

  function upgradePaths(fromId) {
    var from = GPU_CATALOG.filter(function (item) { return item.id === fromId; })[0];
    if (!from) return [];
    var rest = GPU_CATALOG.filter(function (item) { return item.id !== from.id; });
    var family = rest.filter(function (item) { return item.vendor === from.vendor; });
    function gen(item) { return GPU_GENERATION[item.architecture] || 0; }
    var newer = family.filter(function (item) { return gen(item) > gen(from) && item.vram_gb >= from.vram_gb; });
    var value = newer.slice().sort(function (a, b) { return a.watts - b.watts; })[0] || null;
    var balanced = newer.filter(function (item) { return item.architecture === 'Blackwell' && item.vram_gb >= 16; }).sort(function (a, b) { return a.watts - b.watts; })[0] || null;
    var maxVram = rest.reduce(function (best, item) { return item.vram_gb > best ? item.vram_gb : best; }, 0);
    var vram = rest.filter(function (item) { return item.vram_gb === maxVram; }).sort(function (a, b) { return a.watts - b.watts; })[0] || null;
    var performance = family.slice().sort(function (a, b) {
      return gpuScores(b).gaming - gpuScores(a).gaming || b.watts - a.watts;
    })[0] || null;
    return [
      { role: 'Value', product: value },
      { role: 'Balanced', product: balanced },
      { role: 'AI / VRAM', product: vram },
      { role: 'Performance', product: performance }
    ].filter(function (row, index, all) {
      return row.product && all.findIndex(function (other) { return other.product && other.product.id === row.product.id; }) === index;
    });
  }

  function gpuSwapImpact(from, to, cpuWatts, psuWatts) {
    var cpu = Number(cpuWatts) || 0;
    var supply = psuWatts == null ? null : Number(psuWatts);
    var need = cpu + to.watts + 150;
    return {
      vram: [from.vram_gb, to.vram_gb],
      watts: [from.watts, to.watts],
      formulaNeed: need,
      formulaOk: supply == null ? null : supply >= need,
      vendorPsu: to.psu,
      vendorOk: supply == null ? null : supply >= to.psu
    };
  }

  function driveStudy(storageGb, answers) {
    var a = answers || {};
    var cameraOnly = hasJob(a, 'smart') && !hasJob(a, 'files') && !hasJob(a, 'movies') && !hasJob(a, 'photos') && !hasJob(a, 'video');
    var big = Number(storageGb) >= 4000;
    var gb = Number(storageGb) || 0;
    var eachTb = gb < 4000 ? 0 : (gb >= 16000 ? 8 : Math.max(4, Math.round(gb / 1000)));
    var study = {
      title: 'Storage drive trade study',
      requirement: big
        ? 'A NAS drive in the size you picked. CMR. Rated to stay on. SATA. New, or used only if the listing shows the drive is healthy.'
        : 'When you add a pile, use a CMR NAS drive. SATA. New, or used only if the listing shows the drive is healthy.',
      rows: [
        { name: 'Seagate IronWolf', cmr: 'Pass', nas: 'Pass', warranty: '3 years', result: 'Qualifies' },
        { name: 'WD Red Plus', cmr: 'Pass', nas: 'Pass', warranty: '3 years', result: 'Qualifies' },
        { name: 'WD Red Pro', cmr: 'Pass', nas: 'Pass', warranty: '5 years', result: 'Qualifies' },
        { name: 'Plain WD Red, 2 TB to 6 TB', cmr: 'Fail', nas: 'Not the NAS line', warranty: '3 years', result: 'Reject' },
        { name: 'WD Purple', cmr: 'Pass', nas: 'Surveillance, not a file NAS', warranty: '3 years', result: cameraOnly ? 'Qualifies' : 'Reject' },
        { name: 'WD Black', cmr: 'Pass', nas: 'Fail', warranty: '5 years', result: 'Reject' },
        { name: 'Exos', cmr: 'Pass', nas: 'Pass', warranty: '5 years', result: 'Qualifies' }
      ],
      decision: cameraOnly ? 'WD Purple.' : 'Seagate IronWolf or WD Red Plus.',
      requirements: [
        { id: 'R1', text: 'CMR', result: 'Pass' },
        { id: 'R2', text: 'NAS workload rating', result: 'Pass' },
        { id: 'R3', text: 'At least a 3-year warranty', result: 'Pass' },
        { id: 'R4', text: 'Capacity in the size you picked', result: 'Pass' }
      ],
      confidence: 'High. Both qualifying drives meet every mandatory rule. The winner between them is whichever has the lower price on the seller page.',
      why: [
        'Both pass the mandatory checks: CMR, a NAS workload rating, and at least a 3-year warranty.',
        'Buy the one with the lower price on the day you look. This page does not invent that dollar.',
        'Plain WD Red in the 2 TB to 6 TB sizes fails CMR. Western Digital says many of those drives used SMR, and a rebuild does not give an SMR drive the idle time it wants. The lower sticker is how that price goes wrong.',
        'WD Black fails the NAS duty rating. WD Purple is for cameras, so it wins only when the lab is cameras and not a file pile. Exos passes, and it is louder than a house wants.'
      ],
      tradeoff: 'WD Red Pro also passes, and the warranty is 5 years. Pay the extra only if you want that longer warranty.',
      links: [
        { name: 'IronWolf on PCPartPicker', href: 'https://pcpartpicker.com/search/?q=IronWolf%208TB', detail: 'Live price.' },
        { name: 'WD Red Plus on PCPartPicker', href: 'https://pcpartpicker.com/search/?q=WD%20Red%20Plus', detail: 'Live price.' },
        { name: 'WD Red, SMR and CMR', href: 'https://support-en.wd.com/app/answers/detailweb/a_id/29458', detail: 'Why the cheaper Red fails.' }
      ]
    };
    if (eachTb === 8 && !cameraOnly) {
      var scored = scoreTrade(HDD_8TB.map(function (drive) {
        return { id: drive.id, model: drive.model, scores: hddScores(drive), drive: drive };
      }), {
        weights: { price: 30, warranty: 20, noise: 15, performance: 15, reliability: 20 },
        mandatory: [
          { text: 'CMR', pass: function (row) { return row.drive.recording === 'CMR'; } },
          { text: 'SATA', pass: function (row) { return row.drive.interface === 'SATA'; } },
          { text: '8TB', pass: function (row) { return row.drive.capacity_tb >= 8; } },
          { text: 'NAS or enterprise workload', pass: function (row) { return row.drive.workload === 'NAS' || row.drive.workload === 'enterprise'; } }
        ]
      });
      study.rows = scored.rows.map(function (row) {
        var drive = HDD_8TB.filter(function (item) { return item.id === row.id; })[0];
        return { name: row.name + (drive && drive.mpn ? ' ' + drive.mpn : ''), result: row.result, score: row.score, why: row.why };
      });
      study.decision = scored.winner ? scored.winner.name : study.decision;
      study.why = [
        scored.winner ? (scored.winner.name + ' wins the scored rows. Price is not in this score, because no checked offer is stored. A lower shelf price can change the buy.') : 'No drive passed the mandatory rows.',
        'Mandatory rows are CMR, SATA, at least 8TB, and a NAS or enterprise workload. Purple is surveillance. Black is a desktop drive. Both fail that workload rule.',
        'Exos passes and loses on noise. Red Pro’s 5-year warranty outscores the 3-year NAS drives when price is left out.'
      ];
      study.confidence = 'The score uses warranty, noise, performance, and workload. It does not use a shelf price.';
    }
    return study;
  }

  function ceilingOf(budget) {
    if (budget === 200) return { max: 200, label: 'Under $200' };
    if (budget === 500) return { max: 500, label: '$200 to $500' };
    if (budget === 1200) return { max: 1200, label: '$500 to $1,200' };
    if (budget === 'more') return { max: null, label: 'More than $1,200' };
    return { max: null, label: 'You already own the box' };
  }

  function raidPlan(storageGb, answers) {
    var a = answers || {};
    var gb = Number(storageGb) || 0;
    if (gb < 4000) {
      return {
        disks: 1, eachTb: 1, pick: 'No RAID',
        layouts: [{ name: 'No RAID', usable: 'The one disk', loss: '0' }],
        why: 'One disk is enough for this pile. RAID is not a backup. Keep a second copy somewhere else.'
      };
    }
    var four = gb >= 16000;
    var disks = four ? 4 : 2;
    var eachTb = four ? 8 : Math.max(4, Math.round(gb / 1000));
    var raw = disks * eachTb;
    var layouts = [
      { name: 'Stripe', usable: raw + ' TB', loss: '0 disks' },
      { name: 'Mirror pairs', usable: (raw / 2) + ' TB', loss: disks === 2 ? '1 disk' : '1 disk in each pair' },
      { name: 'RAIDZ1', usable: disks >= 3 ? ((disks - 1) * eachTb) + ' TB' : 'Needs 3 disks', loss: '1 disk' },
      { name: 'RAIDZ2', usable: disks >= 4 ? ((disks - 2) * eachTb) + ' TB' : 'Needs 4 disks', loss: '2 disks' },
      { name: 'No RAID', usable: eachTb + ' TB', loss: '0 disks' }
    ];
    var pick = disks >= 4 && (hasJob(a, 'files') || !hasJob(a, 'movies')) ? 'RAIDZ2' : (disks >= 2 ? 'Mirror pairs' : 'No RAID');
    if (disks >= 4 && hasJob(a, 'movies') && !hasJob(a, 'files')) pick = 'RAIDZ1';
    return {
      disks: disks, eachTb: eachTb, pick: pick, layouts: layouts,
      why: pick + ' is the layout that meets the pile with the least waste. A stripe gives you ' + raw + ' TB and loses everything if one disk dies. RAID is not a backup. The backup branch is the second copy.'
    };
  }

  function gatewayStudy(answers) {
    var a = answers || {};
    var needVlan = a.role === 'server' || a.role === 'both' || hasJob(a, 'smart');
    var canBuild = a.skill === 'ok';
    var rows = [
      { name: 'ISP router', vlan: needVlan ? 'Fail' : 'Pass', run: 'Pass' },
      { name: 'UniFi Dream Machine Pro', vlan: 'Pass', run: 'Pass' },
      { name: 'UniFi Cloud Gateway class', vlan: 'Pass', run: 'Pass' },
      { name: 'OPNsense appliance', vlan: 'Pass', run: canBuild ? 'Pass' : 'Fail' },
      { name: 'TP-Link Omada gateway', vlan: 'Pass', run: 'Pass' }
    ];
    var floorOf = {
      'ISP router': 0,
      'UniFi Dream Machine Pro': 350,
      'UniFi Cloud Gateway class': 250,
      'OPNsense appliance': 200,
      'TP-Link Omada gateway': 150
    };
    var ceiling = ceilingOf(a.budget);
    rows.forEach(function (row) {
      var rejected = row.vlan === 'Fail' || row.run === 'Fail';
      row.result = rejected ? 'Reject' : 'Qualifies';
      row.band = (ceiling.max == null || floorOf[row.name] <= ceiling.max) ? 'Fits' : 'Over';
      var score = 0;
      if (!rejected) {
        score = 60;
        if (row.name !== 'ISP router' && row.name !== 'OPNsense appliance') score += 15;
        if (row.name === 'OPNsense appliance') score += 20;
        if (row.name === 'ISP router') score += 10;
        if (!needVlan && row.name !== 'ISP router') score -= 30;
      }
      row.score = score;
      row.cells = [row.name, row.vlan, row.run, row.result, row.band, String(score)];
    });
    var ranked = rows.slice().sort(function (left, right) { return right.score - left.score; });
    var ideal = ranked[0].name;
    var affordable = ranked.filter(function (row) { return row.score > 0 && row.band === 'Fits'; });
    var decision = (affordable[0] || ranked[0]).name;
    return {
      title: 'Gateway trade study',
      columns: ['Candidate', 'VLANs', 'You can run it', 'Result', 'This band', 'Score'],
      floor: floorOf[decision],
      ideal: ideal,
      idealFloor: floorOf[ideal],
      requirement: (needVlan ? 'The lab needs separate networks for servers, guests, or smart devices.' : 'One flat house network is enough.') + ' Class floor for the pick in this band: $' + floorOf[decision] + '. The requirements winner, ignoring the band, is ' + ideal + ' at $' + floorOf[ideal] + '.',
      rows: rows,
      decision: decision,
      requirements: [
        { id: 'R1', text: 'VLANs when the lab has a server or smart devices', result: needVlan ? 'Required' : 'Not required' },
        { id: 'R2', text: 'A custom firewall only if you can fix a bad rule', result: canBuild ? 'Pass' : 'Fail for a custom firewall' }
      ],
      confidence: 'High. The highest score that still passes the mandatory rows wins.',
      why: [
        'ISP router, class floor $0. It unlocks internet on one network. It does not unlock VLANs, PoE, or a controller. Keep it when the house can stay flat.',
        'TP-Link Omada, class floor $150. It unlocks VLANs in the Omada app. Buy the Omada switch and the Omada access point later so they share that app. It does not unlock UniFi gear.',
        'OPNsense, class floor $200. It unlocks VLANs and firewall rules you own. It does not include Wi-Fi or PoE. This rung is only open when you can fix a bad rule. The switch brand then follows the access point, not the firewall.',
        'UniFi Cloud Gateway, class floor $250. It unlocks a UniFi controller. A UniFi switch and a UniFi access point join the same app. Do not add an Omada switch to that controller.',
        'UniFi Dream Machine Pro, class floor $350. Same UniFi family, with the gateway and the controller in one box, including IDS/IPS in that class. Pick this over the Cloud Gateway when the band can hold it. Pick the Cloud Gateway or Omada when it cannot.',
        'Stay in one family. UniFi gateway, UniFi switch, UniFi access point. Or Omada gateway, Omada switch, Omada access point. Mixing the two means two apps.'
      ],
      tradeoff: 'A custom firewall is more flexible. It is also easier to lock yourself out of the house network.',
      links: [
        { name: 'UniFi Dream Machine Pro specs', href: 'https://techspecs.ui.com/unifi/cloud-gateways/udm-pro', detail: 'Official spec.' },
        { name: 'OPNsense', href: 'https://opnsense.org/', detail: 'The firewall project.' },
        { name: 'Omada', href: 'https://www.tp-link.com/us/omada-sdn/', detail: 'The controller family.' }
      ]
    };
  }

  function switchStudy(answers) {
    var a = answers || {};
    var needVlan = a.role === 'server' || a.role === 'both' || hasJob(a, 'smart');
    var needPoe = !!hasJob(a, 'smart');
    var wantFast = Number(a.storage) >= 8000 && (a.role === 'server' || a.role === 'both');
    function row(name, vlan, poe, speed) {
      var fail = (needVlan && vlan === 'Fail') || (needPoe && poe === 'Fail');
      return { cells: [name, vlan, poe, speed, fail ? 'Reject' : 'Qualifies'] };
    }
    var rows = [
      row('Unmanaged', 'Fail', 'Fail', '1 GbE'),
      row('Managed 1 GbE', 'Pass', 'Fail', '1 GbE'),
      row('Managed PoE', 'Pass', 'Pass', '1 GbE'),
      row('Managed 2.5 or 10 GbE', 'Pass', needPoe ? 'Fail' : 'Pass', '2.5 / 10 GbE')
    ];
    var decision = 'Unmanaged';
    if (needPoe) decision = 'Managed PoE';
    else if (needVlan && wantFast) decision = 'Managed 2.5 or 10 GbE';
    else if (needVlan) decision = 'Managed 1 GbE';
    var named = [{ name: 'Uplink to the gateway', poe: false }];
    if (a.role === 'server' || a.role === 'both') named.push({ name: 'Server', poe: false });
    if (a.role === 'everyday' || a.role === 'both') named.push({ name: 'Desk computer', poe: false });
    if (a.role === 'server') named.push({ name: 'The computer you already use to reach the server', poe: false });
    if (hasJob(a, 'smart')) named.push({ name: 'Access point', poe: true });
    var poeClients = named.filter(function (item) { return item.poe; }).length;
    var demand = {
      ports: named.length,
      poeClients: poeClients,
      poeWatts: poeClients * 15.4,
      spare: 2,
      lines: [
        'Named ports: ' + named.length + ' (' + named.map(function (item) { return item.name; }).join(', ') + ').',
        poeClients
          ? 'PoE now: about ' + (poeClients * 15.4) + ' W for ' + poeClients + ' access point, at 802.3af (about 15.4 W).'
          : 'PoE now: none. No access point was requested.',
        'Cameras are not in this count. You did not say how many. Add about 15.4 W and one port for each camera you later name.',
        'Buy a switch with at least ' + (named.length + 2) + ' ports so two later devices have a place. That spare is not a claim that you already own them.'
      ]
    };
    var switchFloor = { 'Unmanaged': 20, 'Managed 1 GbE': 40, 'Managed PoE': 120, 'Managed 2.5 or 10 GbE': 250 };
    rows.forEach(function (row) {
      var rejected = row.cells[4] === 'Reject';
      var score = rejected ? 0 : (row.cells[0] === decision ? 90 : 60);
      row.cells.push(String(score));
    });
    return {
      title: 'Switch trade study',
      columns: ['Candidate', 'VLANs', 'PoE', 'Speed', 'Result', 'Score'],
      floor: switchFloor[decision],
      demand: demand,
      requirement: demand.lines.join(' '),
      rows: rows,
      decision: decision,
      requirements: [
        { id: 'R1', text: 'VLAN support', result: needVlan ? 'Required' : 'Not required' },
        { id: 'R2', text: 'PoE for the access point you asked for', result: needPoe ? ('Required, about ' + demand.poeWatts + ' W') : 'Not required' },
        { id: 'R3', text: 'Faster than 1 GbE', result: wantFast && !needPoe ? 'Preferred' : 'Not required yet' }
      ],
      confidence: 'High. The smallest class that passes every required row wins.',
      why: [
        'A managed switch is for separate networks, not only for "one cable, two networks." People, cameras, guests, and the server should not all sit on one flat LAN.',
        'PoE means the switch feeds power down the cable. Add the device watts. The switch total is smaller than the maximum per port times every port. About 15.4 W for 802.3af, about 30 W for 802.3at.',
        'If PoE and a fast uplink are both wanted, buy the PoE switch for the edge. A 10 GbE link between the server and the NAS can be a later, separate cable. Do not skip PoE to chase 10 GbE.',
        'Match the switch brand to the gateway. UniFi switch when the gateway is UniFi. Omada switch when the gateway is Omada. An OPNsense gateway can sit in front of either family. The access point should be that same family, or you will run two controllers.',
        'Unmanaged is about $20 and unlocks more ports on one network. Managed 1 GbE is about $40 and unlocks VLANs. Managed PoE is about $120 and unlocks power on the cable. Managed 2.5 or 10 GbE is about $250 and unlocks a faster uplink. Those are class floors, not shelf prices.'
      ],
      tradeoff: '10 GbE costs more ports and more power. It is not the default for a house.',
      links: [
        { name: 'PCPartPicker', href: 'https://pcpartpicker.com/products/network-card/', detail: 'Live prices for network parts. This page does not invent one.' }
      ]
    };
  }

  function mediaStudy(answers) {
    var a = answers || {};
    var server = a.role === 'server' || a.role === 'both' || a.flavor === 'proxmox';
    var decision = server || a.skill === 'ok' ? 'Jellyfin' : 'Plex';
    return {
      title: 'Media server trade study',
      columns: ['Requirement', 'Jellyfin', 'Plex', 'Plex Pass'],
      requirement: 'Play the files in the house. The player is not the disk shelf.',
      rows: [
        { cells: ['Basic server', 'Free', 'Free tier', 'Paid'] },
        { cells: ['Hardware transcoding', 'Free', 'Limited', 'Included'] },
        { cells: ['Remote apps', 'Good', 'Excellent', 'Excellent'] },
        { cells: ['Open source', 'Yes', 'No', 'No'] },
        { cells: ['Needs an account', 'No', 'Yes', 'Yes'] },
        { cells: ['Lifetime option', 'No', 'No', 'Yes'] }
      ],
      decision: decision,
      requirements: [
        { id: 'R1', text: 'No subscription for hardware transcoding', result: decision === 'Jellyfin' ? 'Jellyfin passes' : 'Not the deciding row' },
        { id: 'R2', text: 'Easy TV apps for someone new to this', result: decision === 'Plex' ? 'Plex free tier passes' : 'Not required' }
      ],
      confidence: 'High. Money is $0 unless you later choose Plex Pass on Plex’s own plan page.',
      why: [
        decision === 'Jellyfin'
          ? 'Jellyfin wins because hardware transcoding stays free and the server does not need a Plex account.'
          : 'Plex’s free tier wins because the TV apps are the easier path, and this build did not require free hardware transcoding.',
        'Plex Pass is the paid row: monthly, annual, or lifetime. Its price stays on Plex’s plan page. It is not required for a basic server.'
      ],
      tradeoff: 'Plex’s remote apps are smoother. The account and the paid transcoding are the cost of that.',
      links: [
        { name: 'Jellyfin', href: 'https://jellyfin.org/downloads/', detail: 'Free.' },
        { name: 'Plex', href: 'https://support.plex.tv/articles/200288586-installation/', detail: 'Free tier install.' }
      ]
    };
  }

  function spendForecast(answers, gateway, net) {
    var a = answers || {};
    var ceiling = ceilingOf(a.budget);
    var max = ceiling.max;
    function rung(spend, buy, unlocks, open) {
      var money = max == null || spend <= max;
      var allowed = open !== false;
      var note = !allowed ? ' The dollars may fit, but this rung is closed for the reason in the unlock text.' : (money ? ' This band can hold that piece.' : ' This band cannot hold that piece.');
      return {
        spend: spend,
        buy: buy,
        unlocks: unlocks,
        fits: money && allowed,
        line: 'Spend about $' + spend + ' on ' + buy + '. Unlocks: ' + unlocks + note
      };
    }
    var rows = [
      rung(0, 'the ISP router', 'internet on one network. It does not unlock separate networks for guests, cameras, or the server.'),
      rung(150, 'a TP-Link Omada gateway', 'VLANs inside the Omada app. An Omada switch and an Omada access point can join that same app later. It does not unlock UniFi gear.'),
      rung(200, 'an OPNsense appliance', 'VLANs and firewall rules you own. It does not include Wi-Fi or PoE. ' + (a.skill === 'ok' ? 'You can fix a bad rule, so this rung is open.' : 'This rung stays closed until you can fix a bad rule.'), a.skill === 'ok'),
      rung(250, 'a UniFi Cloud Gateway', 'a UniFi controller. A UniFi switch and a UniFi access point join the same app later.'),
      rung(350, 'a UniFi Dream Machine Pro', 'the gateway and the UniFi controller in one box, including IDS/IPS in that class. Same family as the Cloud Gateway.')
    ];
    var sw = net.floor || 0;
    rows.push(rung(sw, 'the ' + net.decision + ' switch class', net.decision === 'Managed PoE'
      ? 'VLAN ports plus power for the access point, about 15.4 W now. Use a UniFi switch with a UniFi gateway, or an Omada switch with an Omada gateway. An OPNsense gateway can sit in front of either.'
      : 'the ports the study asked for. Match the switch brand to the gateway family so the switch and the access point share one app.'));
    if (hasJob(a, 'smart')) {
      rows.push(rung(100, 'a UniFi U6+ class access point', 'Wi-Fi 6, VLAN tagging, and power from the PoE switch. A Wi-Fi 7 U7 class is about $180 and stays closed until the phones you own can use it.'));
    }
    var path = (gateway.idealFloor != null ? gateway.idealFloor : gateway.floor) + sw + (hasJob(a, 'smart') ? 100 : 0);
    rows.push(rung(path, 'the gateway the requirements want, plus the switch' + (hasJob(a, 'smart') ? ', plus the access point' : ''), 'the whole network design: separate networks' + (hasJob(a, 'smart') ? ', powered Wi-Fi, and one controller family' : '') + '. The server is a separate spend on top of this.'));
    if ((a.role === 'server' || a.role === 'both') && a.budget !== 'have') {
      var ramFloor = Number(a.ram) >= 64 ? 120 : (Number(a.ram) >= 32 ? 70 : 40);
      var serverSpend = 100 + 80 + ramFloor + 50 + 60 + 50;
      rows.push(rung(serverSpend, 'the server class (CPU, board, memory, boot drive, power supply, case)', 'a machine that stays on. It does not unlock VLANs or powered Wi-Fi.'));
    }
    return rows;
  }

  function labModel(answers, report) {
    var a = answers || {};
    var raid = raidPlan(a.storage, a);
    var drives = driveStudy(a.storage, a);
    var gateway = gatewayStudy(a);
    var net = switchStudy(a);
    var forecast = spendForecast(a, gateway, net);
    gateway.forecast = forecast;
    net.forecast = forecast;
    var media = (hasJob(a, 'movies') || hasJob(a, 'photos') || hasJob(a, 'video')) ? mediaStudy(a) : null;
    var ceiling = ceilingOf(a.budget);
    var fit = suggestFit(a, raid);
    var checks = fit.lines.map(function (line) { return line.text; });
    checks.push('Fit: ' + (fit.tone === 'go' ? 'the suggested PC parts agree.' : (fit.tone === 'stop' ? 'the suggested PC parts clash.' : 'the suggested PC parts need a closer look.')));
    checks.push('RAID is not a backup. ' + raid.why);
    if (a.role === 'server' || a.role === 'both' || hasJob(a, 'smart')) checks.push('Gateway: ' + gateway.decision + '. Switch: ' + net.decision + '. ' + (net.demand ? net.demand.lines[0] : ''));
    var owns = a.budget === 'have';
    var ramFloor = Number(a.ram) >= 64 ? 120 : (Number(a.ram) >= 32 ? 70 : 40);
    var minimum = 0;
    if (!owns && (a.role === 'server' || a.role === 'both')) minimum += 100 + 80 + ramFloor + 50 + 60 + 50;
    if (a.role === 'server' || a.role === 'both' || hasJob(a, 'smart')) minimum += (gateway.floor || 0) + (net.floor || 0);
    if (hasJob(a, 'smart')) minimum += 100;
    if (raid.disks > 1) minimum += 150 * raid.disks;
    if (!owns && raid.disks >= 4 && (a.role === 'server' || a.role === 'both')) minimum += 40;
    var conflict = ceiling.max != null && minimum > ceiling.max ? {
      minimum: minimum,
      lines: [
        'This design cannot be built for ' + ceiling.label + '.',
        'Class-floor minimum: about $' + minimum + '.',
        'Option A: raise the budget.',
        'Option B: reuse the router and the server you already own.',
        'Option C: build the server first. Add managed networking later.'
      ]
    } : null;
    var summary = [
      conflict ? conflict.lines.join(' ') : 'The class-floor total fits the band you picked, or you already own the box.',
      'A class floor is budget math, dated Sep 24, 2026. It is not a live shelf price.',
      'Ceiling: ' + ceiling.label + '.',
      'Drives: ' + drives.decision,
      'Layout: ' + raid.pick + ' across ' + raid.disks + ' disk' + (raid.disks === 1 ? '' : 's') + '.'
    ].concat(checks);
    if (media) summary.push('Player: ' + media.decision + '.');
    summary.push((raid.disks >= 4 || Number(a.gpu) >= 16) ? 'Build status: open. A compatibility check above is still waiting on a part you choose.' : 'Build status: the decisions that can be made from your answers are made. Prices are still yours to enter.');
    var codename = hasJob(a, 'ai') ? 'Project Rex' : (hasJob(a, 'games') ? 'Project Arsenal' : ((hasJob(a, 'smart') && (a.role === 'server' || a.role === 'both')) ? 'Project Warden' : (hasJob(a, 'files') || hasJob(a, 'movies') ? 'Project Haven' : 'Project Outer Heaven')));
    return { ceiling: ceiling, raid: raid, drives: drives, gateway: gateway, switchPick: net, media: media, fit: fit, forecast: forecast, conflict: conflict, recommended: minimum, codename: codename, summary: summary };
  }

  function characterSheet(tree, answers) {
    var a = answers || {};
    var slots = [];
    var traits = [];
    function walk(node, ancestors) {
      var next = ancestors.concat([node]);
      (node.children || []).forEach(function (child) { walk(child, next); });
      if (node.children && node.children.length) return;
      var proposed = node.status === 'selected' || node.status === 'over' || node.status === 'ready' || node.status === 'recommended';
      var empty = node.status === 'skip' && node.offer && node.offer.noteOnly;
      var open = node.status === 'need' && node.offer;
      if (!proposed && !empty && !open) return;
      if (proposed && !node.offer) {
        traits.push(node.title);
        return;
      }
      var l2 = ancestors.filter(function (item) { return item.level === 'L2'; }).pop();
      var l3 = ancestors.filter(function (item) { return item.level === 'L3'; }).pop();
      var l4 = ancestors.filter(function (item) { return item.level === 'L4'; }).pop();
      var slot = (l2 && l2.title === 'Network' && l3) ? l3.title : (l4 ? l4.title : node.title);
      var floor = null;
      if (node.offer) {
        if (node.offer.dollars === 0) floor = 0;
        else if (node.offer.floor != null) floor = node.offer.floor;
      }
      slots.push({
        id: node.id,
        slot: slot,
        item: node.title,
        group: (node.offer && node.offer.group) || 'Design',
        qty: (node.offer && node.offer.qty) || 1,
        floor: floor,
        noteOnly: !!(node.offer && node.offer.noteOnly),
        status: node.status
      });
    }
    walk(tree, []);
    var cpu = slots.filter(function (slot) { return slot.slot === 'CPU'; })[0];
    var gate = slots.filter(function (slot) { return slot.slot === 'Gateway'; })[0];
    var klass = a.role === 'server' ? 'Closet server' : (a.role === 'both' ? 'One-box lab' : 'Desk');
    var signature = [cpu && cpu.item, gate && gate.item].filter(Boolean).join(' · ');
    return {
      klass: klass,
      name: signature || klass,
      slots: slots,
      traits: traits,
      priceNote: 'These dollars are class floors dated Sep 24, 2026. They do not change when a store changes its price. The source is the class table in this lesson, not a live feed. Check PCPartPicker, then type the price you saw. That typed price replaces the floor.'
    };
  }

  function settleBuild(tree, record) {
    var stored = (record && record.items) || {};
    var leaves = [];
    function visit(node, ancestors) {
      var kids = node.children || [];
      if (!kids.length) {
        leaves.push({ node: node, ancestors: ancestors });
        return;
      }
      kids.forEach(function (child) { visit(child, ancestors.concat([node])); });
    }
    if (tree) visit(tree, []);

    function moneyKind(node) {
      if (!node.offer || node.offer.noteOnly) return 'design';
      if (node.offer.dollars === 0) return 'free';
      if (node.offer.floor != null) return 'planning';
      return 'unpriced';
    }

    function baseState(node) {
      if (node.status === 'recommended' || node.status === 'ready' || node.status === 'selected' || node.status === 'over') return 'recommended';
      return 'skipped';
    }

    var recommended = [];
    var actual = [];
    var known = 0;
    var unpriced = 0;
    var groups = {};
    leaves.forEach(function (row) {
      var node = row.node;
      var saved = stored[node.id];
      var state = saved && saved.state ? saved.state : baseState(node);
      if (state !== 'recommended' && state !== 'equipped' && state !== 'owned' && state !== 'skipped') state = 'skipped';
      var offerQty = node.offer && node.offer.qty ? node.offer.qty : 1;
      var quantity = saved && saved.quantity ? saved.quantity : offerQty;
      var entry = {
        id: node.id,
        title: node.title,
        state: state,
        quantity: quantity,
        ancestors: row.ancestors.map(function (parent) { return parent.id; }),
        slot: row.ancestors.length ? row.ancestors[row.ancestors.length - 1].title : node.title,
        group: (node.offer && node.offer.group) || 'Design',
        kind: moneyKind(node),
        planning: node.offer && node.offer.floor != null ? node.offer.floor : (node.offer && node.offer.dollars === 0 ? 0 : null),
        actual: saved && saved.actual != null && saved.actual !== '' && !isNaN(Number(saved.actual)) ? Number(saved.actual) : null
      };
      if (state === 'recommended') recommended.push(entry);
      if (state !== 'equipped' && state !== 'owned') return;
      actual.push(entry);
      var amount = null;
      if (state === 'owned' || entry.kind === 'free' || entry.kind === 'design') amount = 0;
      else if (entry.actual != null) amount = entry.actual * entry.quantity;
      else if (entry.kind === 'planning') amount = entry.planning * entry.quantity;
      if (!groups[entry.group]) groups[entry.group] = { known: 0, unpriced: 0 };
      if (amount == null) {
        unpriced += 1;
        groups[entry.group].unpriced += 1;
      } else {
        known += amount;
        groups[entry.group].known += amount;
      }
    });

    var cap = tree && tree.model && tree.model.ceiling;
    var max = cap && cap.max != null ? cap.max : null;
    var status = unpriced > 0 ? 'incomplete' : (max != null && known > max ? 'over' : 'priced');
    var before = max == null ? null : (max - known);
    var line;
    if (unpriced > 0 && before != null && before < 0) line = 'Known selected cost is $' + (known - max) + ' over the ceiling, before unpriced items. Final remaining: UNKNOWN.';
    else if (unpriced > 0 && before != null) line = '$' + before + ' remains before unpriced items. Final remaining: UNKNOWN.';
    else if (unpriced > 0) line = 'Final remaining: UNKNOWN.';
    else if (before != null && before < 0) line = '$' + (known - max) + ' over the ceiling.';
    else if (before != null) line = 'Known remaining $' + before + '.';
    else line = 'This band has no ceiling. Known selected cost $' + known + '.';

    var slots = [];
    function collect(node) {
      if (node.required && node.slotId && node.children && node.children.length) slots.push(node);
      (node.children || []).forEach(collect);
    }
    if (tree) collect(tree);
    var filled = 0;
    var missing = [];
    slots.forEach(function (slot) {
      var ok = actual.some(function (item) { return item.ancestors.indexOf(slot.id) !== -1; });
      if (ok) filled += 1;
      else missing.push(slot.slotId);
    });
    var unresolved = [];
    function findTitle(node, title) {
      if (!node) return null;
      if (node.title === title) return node;
      var kids = node.children || [];
      for (var i = 0; i < kids.length; i++) {
        var hit = findTitle(kids[i], title);
        if (hit) return hit;
      }
      return null;
    }
    var backup = findTitle(tree, 'Backup');
    if (backup && !actual.some(function (item) { return item.ancestors.indexOf(backup.id) !== -1; })) unresolved.push('Backup target not equipped');
    var tone = tree && tree.model && tree.model.fit && tree.model.fit.tone;
    var checks = [];
    if (tone === 'stop') {
      checks.push('Compatibility does not pass.');
      unresolved.push('Suggested PC parts clash');
    } else if (tone === 'wait') {
      checks.push('Compatibility still needs a closer look.');
      unresolved.push('Compatibility still needs a closer look');
    } else if (tone === 'go') checks.push('Suggested PC parts agree.');
    if (unpriced > 0) unresolved.push(unpriced + ' selected ' + (unpriced === 1 ? 'item still needs' : 'items still need') + ' a price');
    return {
      version: 1,
      name: (record && record.name) || (tree && tree.model && tree.model.codename) || 'Your lab',
      recommendedBuild: { items: recommended },
      actualBuild: { items: actual },
      groups: groups,
      budget: {
        known: known,
        unpriced: unpriced,
        estimated: tree && tree.model ? tree.model.recommended : null,
        status: status,
        line: line,
        ceiling: max,
        beforeUnpriced: before,
        finalRemaining: unpriced > 0 || before == null ? null : before
      },
      readiness: {
        percent: slots.length ? Math.round((filled / slots.length) * 100) : 100,
        filled: filled,
        required: slots.length,
        missing: missing,
        unresolved: unresolved,
        checks: checks
      }
    };
  }

  function labBreakdown(answers, report) {
    var a = answers || {};
    report = report || explain(a);
    var pick = report.pick;
    var serverPick = pick === 'proxmox' || pick === 'ubuntu' || pick === 'alpine' || pick === 'macmini';
    var wantServer = a.role === 'server' || a.role === 'both' || serverPick || pick === 'maclab';
    var wantDesk = a.role !== 'server' || a.role === 'both' || !serverPick;
    if (a.role === 'server' && serverPick) wantDesk = false;
    if (a.role === 'everyday' && !serverPick && pick !== 'maclab') wantServer = false;
    function nest(id, title, product) {
      product.level = 'L5';
      return branch(id, 'L4', title, [product]);
    }
    function req(node, slotId, required) {
      node.slotId = slotId;
      node.required = !!required;
      return node;
    }
    var model = labModel(a, report);
    function hw(id, asm, pickTitle, status, floor, line, sections) {
      var owns = a.budget === 'have';
      var useFloor = owns ? 0 : floor;
      var st = status;
      if (st === 'ready' || st === 'selected' || st === 'over') st = 'recommended';
      var offer = st === 'skip'
        ? { group: 'Server', name: pickTitle, dollars: 0, noteOnly: true, qty: 1 }
        : { group: 'Server', name: pickTitle, dollars: owns ? 0 : null, floor: useFloor, qty: id === 'datadisks' ? Math.max(1, model.raid.disks) : 1, retailer: 'PCPartPicker', checked: 'Sep 24, 2026' };
      var body = sections || [
        note('Why', [line], 'why'),
        note('Where to buy it', [{ name: 'PCPartPicker', href: 'https://pcpartpicker.com/search/?q=' + encodeURIComponent(pickTitle), detail: 'Live price. A class floor is not a shelf price.' }], 'buy')
      ];
      return nest(id, asm, tag(leaf(id + '-pick', 'L5', pickTitle, line, body), 'hardware', offer, st));
    }
    var computeKids = [];
    var os = osLeaf(report, 'L5');
    var osOnServer = serverPick || a.role === 'server';
    if (wantServer) {
      computeKids.push(branch('server', 'L3', 'Server', [
        osOnServer
          ? nest(pick === 'proxmox' ? 'hypervisor' : 'host', pick === 'proxmox' ? 'Hypervisor' : 'Host', os)
          : nest('host', 'Host', leaf('server-os', 'L5', 'Server system', report.labLine || 'A second computer that stays on.', [])),
        req(hw('case', 'Case', model.fit.case ? model.fit.case.name : 'Case', 'selected', 50, model.fit.case ? model.fit.case.plain : 'Match the board. A Micro-ATX case does not take an E-ATX board.'), 'case', true),
          req(hw('board', 'Motherboard', model.fit.board ? model.fit.board.name : 'Motherboard', 'selected', 80, model.fit.board ? model.fit.board.plain : 'The board must match the CPU socket.', [
            note('Why', ['Socket, RAM generation, SATA count, and PCIe slots are decided here.'].concat(model.fit.lines.map(function (line) { return line.text; })), 'why'),
            { name: 'Check fit', slot: 'compare', lines: ['Six kinds of part. Green fits, red clashes, yellow needs a closer look.'], panel: 'build' },
            note('Where to buy it', [{ name: 'PCPartPicker', href: 'https://pcpartpicker.com/', detail: 'Live price. A class floor is not a shelf price.' }], 'buy')
          ]), 'motherboard', true),
          req(hw('cpu', 'CPU', model.fit.cpu ? model.fit.cpu.name : '65W class CPU', 'selected', 100, model.fit.cpu ? model.fit.cpu.plain : 'A 65W desktop CPU. The board has to use that socket.'), 'cpu', true),
          hw('cooler', 'CPU cooler', 'Included cooler', 'skip', 0, 'Use the cooler in the CPU box unless the case is too short for it.'),
          req(hw('ram', 'RAM', model.fit.ram ? model.fit.ram.name : ((a.ram || 16) + ' GB'), 'selected', Number(a.ram) >= 64 ? 120 : (Number(a.ram) >= 32 ? 70 : 40), model.fit.ram ? model.fit.ram.plain : report.hardware.ram), 'ram', true),
          hw('gpubom', 'GPU', model.fit.gpu ? model.fit.gpu.name : 'No extra card', model.fit.gpu && model.fit.gpu.id !== 'none' ? 'need' : 'skip', 0, model.fit.gpu ? model.fit.gpu.plain : report.hardware.gpuLabel),
          req(hw('psu', 'PSU', model.fit.psu ? model.fit.psu.name : 'Power supply', 'selected', 60, model.fit.psu ? model.fit.psu.plain : 'Add the CPU watts, the card watts, and about 150 W.'), 'psu', true),
          req(hw('bootssd', 'Boot drive', 'NVMe boot', 'selected', 50, 'The system lives here. The pile does not.'), 'boot', true),
          hw('datadisks', 'Data drives', model.drives.decision, model.raid.disks > 1 ? 'selected' : 'skip', 150, model.raid.why),
          hw('nic', 'NIC', (model.switchPick.decision.indexOf('10') !== -1 || model.switchPick.decision.indexOf('2.5') !== -1) ? 'Faster NIC' : 'Onboard Ethernet', (model.switchPick.decision.indexOf('10') !== -1 || model.switchPick.decision.indexOf('2.5') !== -1) ? 'need' : 'skip', 0, 'Onboard Ethernet is enough until the switch study asks for more than 1 GbE.'),
          hw('wifi', 'Wi-Fi', 'Not required', 'skip', 0, 'A server should use a cable. Wi-Fi belongs on an access point.'),
          hw('sound', 'Sound', 'Not required', 'skip', 0, 'Not required on this lab box.'),
          hw('fans', 'Fans', 'Case fans', 'need', 0, 'Start with the fans that come with the case.'),
          hw('hba', 'HBA', model.raid.disks >= 4 ? 'HBA or extra SATA' : 'Not required', model.raid.disks >= 4 ? 'selected' : 'skip', model.raid.disks >= 4 ? 40 : 0, 'Four or more SATA disks need four ports, or an HBA. A Micro-ATX board often does not have four.'),
          nest('ups', 'UPS', tag(leaf('ups-pick', 'L5', 'UPS', 'A short outage should park the disks.', [
            note('Add to build', ['Add it when this machine must stay up through a flicker.'], 'add'),
            note('Skip', ['Skip it only if this machine can go dark without hurting the only copy of the files.'], 'skip')
          ]), 'optional', null, 'need'))
      ]));
    }
    if (wantDesk) {
      var deskProduct = osOnServer
        ? leaf('desk-os', 'L5', 'Desk system', 'The computer you sit at. It is not the server.', [])
        : os;
      computeKids.push(branch('desktop', 'L3', 'Desktop', [nest('desk-host', 'Host', deskProduct)]));
    }
    if (a.side !== 'mac') {
      var gpuWant = Number(a.gpu) || 0;
      var gpuPick = !gpuWant ? '' : (gpuWant <= 8 ? 'rtx-4060-8' : (gpuWant <= 12 ? 'rtx-5070-12' : (gpuWant <= 16 ? 'rtx-5070ti-16' : 'rtx-3090-24')));
      if (gpuWant >= 24 && !hasJob(a, 'ai')) gpuPick = 'rtx-4090-24';
      function gpuModel(product) {
        var node = leaf('gpu-' + product.id, 'L5', product.model, product.architecture + ' · ' + product.vram_gb + ' GB ' + product.memory + ' · ' + product.watts + ' W', [
          note('Why it matters', ['A newer architecture can raise performance per watt, encoding, and features. It does not replace VRAM. A 24 GB older card can still hold a larger local model than a newer 12 GB card.'], 'why')
        ]);
        node.product = product;
        var chosen = product.id === gpuPick;
        return tag(node, 'hardware', { group: 'Server', name: product.model, dollars: null, qty: 1, productId: product.id }, chosen ? 'recommended' : null);
      }
      function gpuFamily(id, title, architecture) {
        return branch('gpu-' + id, 'L4', title, GPU_CATALOG.filter(function (product) { return product.architecture === architecture; }).map(gpuModel));
      }
      var gpuKids = [
        gpuFamily('ampere', 'Ampere', 'Ampere'),
        gpuFamily('ada', 'Ada Lovelace', 'Ada Lovelace'),
        gpuFamily('blackwell', 'Blackwell', 'Blackwell'),
        gpuFamily('rdna2', 'RDNA 2', 'RDNA 2'),
        gpuFamily('rdna3', 'RDNA 3', 'RDNA 3'),
        gpuFamily('alchemist', 'Alchemist', 'Alchemist'),
        gpuFamily('battlemage', 'Battlemage', 'Battlemage')
      ];
      if (!gpuWant) gpuKids.unshift(nest('card', 'No extra card', tag(leaf('gpu-none', 'L5', 'No extra card', 'Use the picture built into the processor, or reach this machine from another screen.', []), 'architecture', null, 'recommended')));
      computeKids.push(branch('gpu', 'L3', 'GPU', gpuKids));
    }
    var subsystems = [branch('compute', 'L2', 'Compute', computeKids)];
    function layoutNode(name) {
      var chosen = name === model.raid.pick;
      var row = model.raid.layouts.filter(function (item) { return item.name === name; })[0] || { usable: '', loss: '' };
      return nest(name.toLowerCase().replace(/\s+/g, '-'), name, tag(leaf(name.toLowerCase().replace(/\s+/g, '-') + '-pick', 'L5', name, row.usable + '. Failures tolerated: ' + row.loss + '.', [
        note('Why', [model.raid.why], 'why'),
        note('Risks', ['RAID is not a backup. A mirror survives a dead disk. It does not survive a fire, a theft, or a delete.'], 'risks')
      ]), 'architecture', null, chosen ? 'recommended' : 'skip'));
    }
    var storageKids = [
      branch('boot', 'L3', 'Boot storage', [
        nest('nvme', 'NVMe', tag(leaf('boot-nvme', 'L5', 'NVMe boot', wantServer ? 'Counted on the server boot drive. Do not buy a second one for the same machine.' : 'The system and the apps. M.2 is the shape. NVMe is the speed.', [
          note('Why', ['The operating system and a player database belong on an SSD.'], 'why'),
          note('Compare', ['Some M.2 slots are SATA, not NVMe. Read the slot before you buy.'], 'compare'),
          note('Where to buy it', [{ name: 'PCPartPicker', href: 'https://pcpartpicker.com/search/?q=NVMe%20SSD', detail: 'Live price.' }], 'buy')
        ]), 'hardware', wantServer ? null : { group: 'Storage', name: 'NVMe boot', dollars: null, floor: 50 }, wantServer ? 'skip' : 'selected')),
        nest('sata-boot', 'SATA SSD', tag(leaf('boot-sata', 'L5', 'SATA boot SSD', 'Use this when the board has no NVMe slot.', [
          note('Why', ['SATA SSD still beats a spinning disk for the system.'], 'why')
        ]), 'hardware', null, 'skip'))
      ])
    ];
    if (hasJob(a, 'movies') || hasJob(a, 'photos') || hasJob(a, 'files') || hasJob(a, 'video') || Number(a.storage) >= 4000) {
      storageKids.push(branch('bulk', 'L3', 'Bulk storage', [
        nest('drives', 'Hard drives', tag(leaf('drive-pick', 'L5', 'Drive family', 'CMR disks for the pile. The system stays on the SSD.', [
          note('Why', ['The NAS holds the large files. The server runs the apps.'], 'why'),
          note('Compare', ['Same house network as the desk. Do not forward the admin page to the internet.'], 'compare'),
          { name: 'Trade study', slot: 'study', lines: [], study: model.drives },
          note('Where to buy it', model.drives.links, 'buy')
        ]), 'hardware', { group: 'Storage', name: model.drives.decision, dollars: null }, 'recommended')),
        nest('cmr', 'CMR', tag(leaf('cmr-pick', 'L5', 'CMR', 'Conventional recording. The kind a rebuild can finish.', [note('Why', ['IronWolf, Red Plus, Red Pro, and Exos are CMR.'], 'why')]), 'architecture', null, 'recommended')),
        nest('smr', 'SMR', tag(leaf('smr-pick', 'L5', 'SMR', 'Shingled recording. Cheaper, and a poor fit for a RAID rebuild.', [note('Why', ['Plain WD Red in the 2 TB to 6 TB sizes often used SMR. That fails this lab.'], 'why')]), 'architecture', null, 'skip')),
        nest('bulk-ssd', 'SATA SSD', tag(leaf('bulk-ssd-pick', 'L5', 'Bulk SATA SSD', 'Right for a small fast pile. Wrong price per terabyte for movies.', [
          note('Why', ['Pick this only when the pile is small and you want it quiet.'], 'why')
        ]), 'hardware', null, 'skip')),
        nest('bulk-nvme', 'NVMe', tag(leaf('bulk-nvme-pick', 'L5', 'Bulk NVMe', 'Too expensive per terabyte for a file shelf.', [
          note('Why', ['Keep NVMe for boot and for a cache, not for the movie pile.'], 'why')
        ]), 'hardware', null, 'skip'))
      ]));
    }
    storageKids.push(branch('cache', 'L3', 'Cache', [
      nest('cache-disk', 'Cache disk', tag(leaf('cache-pick', 'L5', 'Cache later', 'A cache helps when many people open the same files. It is not the first disk you buy.', [
        note('Add to build', ['Add a cache after the pile is already too slow.'], 'add'),
        note('Skip', ['Skip it on the first build.'], 'skip')
      ]), 'optional', null, 'skip'))
    ]));
    var layoutBranch = branch('layout', 'L3', 'RAID / ZFS', [
      layoutNode('Mirror pairs'),
      layoutNode('RAIDZ1'),
      layoutNode('RAIDZ2'),
      layoutNode('No RAID')
    ]);
    var needsLayout = hasJob(a, 'movies') || hasJob(a, 'photos') || hasJob(a, 'files') || hasJob(a, 'video') || Number(a.storage) >= 4000;
    layoutBranch.slotId = 'storage-layout';
    layoutBranch.required = needsLayout;
    storageKids.push(layoutBranch);
    storageKids.push(branch('backup', 'L3', 'Backup', [
      nest('local-copy', 'Local second copy', tag(leaf('local-copy-pick', 'L5', 'Local second copy', 'A second disk in the same room. It survives one disk dying.', [
        note('Why', ['This is the minimum. It does not survive a fire.'], 'why'),
        note('Risks', ['Same shelf, same disaster.'], 'risks')
      ]), 'architecture', null, 'skip')),
      nest('other-machine', 'Another machine', tag(leaf('other-machine-pick', 'L5', 'Another machine', 'A copy on a different computer in the house.', [
        note('Why', ['A dead NAS does not take the only copy with it.'], 'why')
      ]), 'architecture', null, 'selected')),
      nest('offsite', 'Off-site', tag(leaf('offsite-pick', 'L5', 'Off-site copy', 'A disk at another building, or a cloud copy of the files you cannot replace.', [
        note('Why', ['This is the copy that survives the house.'], 'why'),
        note('Where to buy it', [{ name: 'The disk, on PCPartPicker', href: 'https://pcpartpicker.com/search/?q=external%20HDD', detail: 'Live price for the disk. Cloud prices stay on the provider page.' }], 'buy')
      ]), 'hardware', { group: 'Storage', name: 'Off-site disk', dollars: null }, 'need'))
    ]));
    subsystems.push(branch('storage', 'L2', 'Storage', storageKids));
    if (hasJob(a, 'smart') || a.role === 'server' || a.role === 'both') {
      function netPick(id, asm, title, decision) {
        var chosen = title === decision;
        var study = id.indexOf('gate') === 0 ? model.gateway : model.switchPick;
        var floor = chosen ? (study.floor || 0) : 0;
        var st = 'skip';
        if (chosen) st = 'recommended';
        var offer = chosen ? { group: 'Networking', name: title, dollars: floor === 0 ? 0 : null, floor: floor, qty: 1, retailer: 'PCPartPicker', checked: 'Sep 24, 2026' } : null;
        var demandText = study.demand ? ' ' + study.demand.lines.join(' ') : '';
        return nest(id, asm, tag(leaf(id + '-pick', 'L5', title, chosen ? 'Highest score that passes the mandatory rows. Class floor $' + floor + '.' + demandText : 'Lower score. It stays in the study.', [
          { name: 'Trade study', slot: 'study', lines: [], study: study },
          note('Risks', ['Do not forward Proxmox, the NAS, Remote Desktop, or Home Assistant to the internet.'], 'risks')
        ]), 'architecture', offer, st));
      }
      var gatewayBranch = branch('gateway', 'L3', 'Gateway', [
          netPick('gate-isp', 'ISP router', 'ISP router', model.gateway.decision),
          netPick('gate-pro', 'Prosumer gateway', 'UniFi Dream Machine Pro', model.gateway.decision),
          netPick('gate-cloud', 'Cloud gateway', 'UniFi Cloud Gateway class', model.gateway.decision),
          netPick('gate-opn', 'Custom firewall', 'OPNsense appliance', model.gateway.decision),
          netPick('gate-omada', 'Omada', 'TP-Link Omada gateway', model.gateway.decision)
        ]);
      gatewayBranch.slotId = 'gateway';
      gatewayBranch.required = true;
      subsystems.push(branch('network', 'L2', 'Network', [
        gatewayBranch,
        branch('switching', 'L3', 'Switching', [
          netPick('sw-un', 'Unmanaged', 'Unmanaged', model.switchPick.decision),
          netPick('sw-l2', 'Managed L2', 'Managed 1 GbE', model.switchPick.decision),
          netPick('sw-poe', 'PoE', 'Managed PoE', model.switchPick.decision),
          netPick('sw-fast', 'Faster uplink', 'Managed 2.5 or 10 GbE', model.switchPick.decision)
        ]),
        branch('wireless', 'L3', 'Wireless', [
          nest('ap', 'Wi-Fi AP', tag(leaf('ap-pick', 'L5', hasJob(a, 'smart') ? 'UniFi U6+ class' : 'Not required', hasJob(a, 'smart') ? 'One Wi-Fi 6 access point, PoE, VLAN tagging. Wi-Fi 7 is not required until the clients you own can use it. Class floor $100.' : 'The server uses a cable. Do not buy an access point for the server itself.', [
            note('Why', ['Coverage is one ceiling per floor in a normal house. PoE comes from the switch study. Wi-Fi 7 waits until the phones can use it.'], 'why'),
            note('Trade study', ['UniFi U6+ class: Wi-Fi 6, PoE, VLAN, class floor $100. UniFi U7 Pro class: Wi-Fi 7, PoE, VLAN, class floor $180. The U6+ class wins because Wi-Fi 7 is not a requirement yet.'], 'study')
          ]), hasJob(a, 'smart') ? 'hardware' : 'architecture', hasJob(a, 'smart') ? { group: 'Networking', name: 'UniFi U6+ class', dollars: null, floor: 100 } : { group: 'Networking', name: 'Wi-Fi', dollars: 0, noteOnly: true }, hasJob(a, 'smart') ? 'recommended' : 'skip'))
        ]),
        branch('vlans', 'L3', 'VLANs', [
          nest('vlan-trusted', 'Trusted', tag(leaf('vlan-trusted-pick', 'L5', 'Trusted', 'Phones and the desk. The firewall allows this VLAN to start connections. It does not allow IoT or cameras to start a connection back.', [note('Why', ['Trusted may reach the server. The other VLANs may not reach trusted.'], 'why')]), 'architecture', null, 'selected')),
          nest('vlan-iot', 'IoT', tag(leaf('vlan-iot-pick', 'L5', 'IoT', 'Plugs and bulbs. They may reach the internet. They may not open a connection to the server admin page.', [note('Why', ['Block IoT from starting sessions into trusted or servers.'], 'why')]), 'architecture', null, hasJob(a, 'smart') ? 'selected' : 'skip')),
          nest('vlan-cam', 'Cameras', tag(leaf('vlan-cam-pick', 'L5', 'Cameras', 'Cameras may write to the NAS. They may not join the desk VLAN.', [note('Why', ['Allow cameras to the storage address only.'], 'why')]), 'architecture', null, hasJob(a, 'smart') ? 'selected' : 'skip')),
          nest('vlan-guest', 'Guests', tag(leaf('vlan-guest-pick', 'L5', 'Guests', 'Internet only. No path to the lab.', [note('Why', ['Drop guest traffic toward every other VLAN.'], 'why')]), 'architecture', null, 'selected')),
          nest('vlan-servers', 'Servers', tag(leaf('vlan-servers-pick', 'L5', 'Servers', 'Proxmox and the NAS answer here. Do not publish their admin pages on the WAN.', [note('Why', ['Servers accept connections from trusted. They do not accept new connections from IoT, cameras, or guests.'], 'why')]), 'architecture', null, 'selected'))
        ]),
        branch('cabling', 'L3', 'Cabling', [
          nest('cat6', 'Cat6', tag(leaf('cat6-pick', 'L5', 'Cat6', 'Enough for 1 GbE in a house. Class floor $15.', [note('Why', ['Cat6 is the default cable.'], 'why')]), 'hardware', { group: 'Networking', name: 'Cat6', dollars: null, floor: 15 }, model.switchPick.decision.indexOf('10') === -1 ? 'recommended' : 'skip')),
          nest('cat6a', 'Cat6a', tag(leaf('cat6a-pick', 'L5', 'Cat6a', 'Use this when a run must carry 10 GbE. Class floor $25.', [note('Why', ['Cat6a is for the fast uplink, not for every phone.'], 'why')]), 'hardware', { group: 'Networking', name: 'Cat6a', dollars: null, floor: 25 }, model.switchPick.decision.indexOf('10') !== -1 ? 'recommended' : 'skip')),
          nest('fiber', 'Fiber', tag(leaf('fiber-pick', 'L5', 'Fiber or DAC', 'A short DAC between the server and the switch, or fiber when the run is long.', [note('Why', ['This is a later link, not the first cable in the house.'], 'why')]), 'hardware', null, 'skip'))
        ])
      ]));
    }
    if (hasJob(a, 'ai') || hasJob(a, 'learn')) {
      subsystems.push(branch('ai', 'L2', 'AI', [
        branch('models', 'L3', 'Local models', [
          nest('runtime', 'Runtime', tag(leaf('ollama', 'L5', 'Ollama', 'Local chat. One model that fits the memory. The software is free.', [
          note('Why', [report.hardware.models], 'why'),
          note('Install', ['Install Ollama. Pull one model. Do not download three on the first day.', { name: 'Ollama', href: 'https://ollama.com/download', detail: 'The chat runtime.' }], 'install'),
          note('Models', ['One model that fits the memory. A bigger download is not a better lab.'], 'compare'),
          note('Requirements', [report.hardware.models], 'requirements'),
          asSlot(lessonNote(report, 'sampling', 'Sampling'), 'compare'),
          asSlot(lessonNote(report, 'modelfile', 'Change a model'), 'compare'),
          asSlot(lessonNote(report, 'adam', 'Adam'), 'compare')
        ]), 'free-software', { group: 'Software', name: 'Ollama', dollars: 0 }, 'ready'))
        ])
      ]));
    }
    if (hasJob(a, 'movies') || hasJob(a, 'photos') || hasJob(a, 'video')) {
      subsystems.push(branch('media', 'L2', 'Media', [
        branch('library', 'L3', 'Library', [
          nest('jellyfin', 'Jellyfin', tag(leaf('jellyfin-pick', 'L5', 'Jellyfin', 'Free. Hardware transcoding stays free. No account.', [
            note('Why', ['This is the pick when the lab should not pay for transcoding.'], 'why'),
            note('Install', [{ name: 'Jellyfin', href: 'https://jellyfin.org/downloads/', detail: 'The free player.' }], 'install'),
            { name: 'Trade study', slot: 'compare', lines: [], study: model.media }
          ]), 'free-software', { group: 'Software', name: 'Jellyfin', dollars: 0 }, model.media && model.media.decision === 'Jellyfin' ? 'ready' : 'skip')),
          nest('plex', 'Plex', tag(leaf('plex-pick', 'L5', 'Plex', 'Free tier. The TV apps are the easy path. Hardware transcoding is limited.', [
            note('Why', ['Pick the free tier when the apps matter more than free transcoding.'], 'why'),
            note('Install', [{ name: 'Plex install', href: 'https://support.plex.tv/articles/200288586-installation/', detail: 'The official install note.' }], 'install'),
            { name: 'Trade study', slot: 'compare', lines: [], study: model.media }
          ]), 'free-software', { group: 'Software', name: 'Plex', dollars: 0 }, model.media && model.media.decision === 'Plex' ? 'ready' : 'skip')),
          nest('plex-pass', 'Plex Pass', tag(leaf('plex-pass-pick', 'L5', 'Plex Pass', 'Paid. Monthly, annual, or lifetime. The price stays on Plex’s plan page.', [
            note('License', ['Plex Pass is the paid row. It is not required to play files in the house.'], 'license'),
            note('Cost', ['Monthly, annual, or lifetime. Read the current price on Plex’s plan page. This page does not invent it.'], 'cost'),
            { name: 'Trade study', slot: 'compare', lines: [], study: model.media }
          ]), 'paid-software', null, 'skip'))
        ])
      ]));
    }
    if (hasJob(a, 'smart')) {
      subsystems.push(branch('smart', 'L2', 'Smart home', [
        branch('control', 'L3', 'House control', [
          nest('controller', 'Controller', tag(leaf('ha', 'L5', 'Home Assistant', 'Lights, sensors, and voice. The admin page stays in the house. The software is free.', [
          note('Why', ['One place for the house devices, on a machine that stays on.'], 'why'),
          note('Install', [{ name: 'Home Assistant', href: 'https://www.home-assistant.io/installation/', detail: 'The official install.' }], 'install'),
          asSlot(lessonNote(report, 'home assistant', 'How to run it'), 'install'),
          note('Requirements', ['The admin page stays on the house side of the gateway.'], 'requirements')
        ]), 'free-software', { group: 'Software', name: 'Home Assistant', dollars: 0 }, 'ready'))
        ])
      ]));
    }
    if (hasJob(a, 'games')) {
      var games = subsystems.filter(function (item) { return item.id === 'compute'; })[0];
      if (games) games.children.push(branch('games', 'L3', 'Games', [
        nest('play', 'Play', tag(leaf('game-stack', 'L5', 'Game stack', report.hardware.games, [
          asSlot(lessonNote(report, 'proton', 'Proton'), 'why'),
          asSlot(lessonNote(report, 'driver', 'Graphics drivers'), 'install')
        ]), 'free-software', { group: 'Software', name: 'Proton', dollars: 0 }, 'ready'))
      ]));
    }
    var tree = branch('lab', 'L1', 'Your lab', subsystems);
    tree.model = model;
    tree.sheet = characterSheet(tree, a);
    var settled = settleBuild(tree, { version: 1, name: '', items: {} });
    tree.recommendedBuild = settled.recommendedBuild;
    tree.actualBuild = settled.actualBuild;
    tree.readiness = settled.readiness;
    return tree;
  }

  return {
    FLAVORS: FLAVORS,
    stepsFor: stepsFor,
    flavorChoices: flavorChoices,
    explain: explain,
    topicBoard: topicBoard,
    checkParts: checkParts,
    labBreakdown: labBreakdown,
    settleBuild: settleBuild,
    scoreTrade: scoreTrade,
    sizeSwitch: sizeSwitch,
    acceptImport: acceptImport,
    hddCatalog: function () { return HDD_8TB; },
    gpuCatalog: function () { return GPU_CATALOG; },
    markets: function () { return MARKETS; },
    marketOffers: marketOffers,
    upgradePaths: upgradePaths,
    gpuSwapImpact: gpuSwapImpact,
    gpuScores: gpuScores,
    mount: mount
  };
});
