export const SIDEARMS_WEAPONS = [
  "Classic",
  "Shorty",
  "Frenzy",
  "Ghost",
  "Sheriff",
];

export const SMGS = [
    "Stinger",
    "Spectre"
];

export const RIFLES = [
    "Bulldog",
    "Guardian",
    "Phantom",
    "Vandal"
];

export const SNIPERS = [
    "Marshal",
    "Operator"
];

export const SHOTGUNS = [
    "Bucky",
    "Judge"
];

export const MACHINE_GUNS = [
    "Ares",
    "Odin"
];

export const MELEE = [
    "Melee"
];

export const FAVOURITE_WEAPONS = [
    "Sheriff",
    "Phantom",
    "Vandal",
    "Melee"
];

export const filterWeapons = (weapons, type) => {
  return Object.values(weapons).filter((w) => type.includes(w.weapon));
};
