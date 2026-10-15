package io.github.brooswitminecraft.__MOD_ID__;

import org.slf4j.Logger;

import com.mojang.logging.LogUtils;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;

/**
 * Entry point for __MOD_NAME__. Registers the mod with no gameplay logic;
 * add your own event listeners, registries, and config here.
 */
@Mod(__MOD_CLASS__Mod.MODID)
public class __MOD_CLASS__Mod {
    public static final String MODID = "__MOD_ID__";
    public static final Logger LOGGER = LogUtils.getLogger();

    public __MOD_CLASS__Mod(IEventBus modEventBus, ModContainer modContainer) {
        LOGGER.info("__MOD_NAME__ loaded");
    }
}
