<template>
    <div class="player" @click="$emit('openModal', PlayerLoadout)">
        <div class="player_name">
            <span>{{ PlayerLoadout.Name }}</span>
        </div>
    </div>
</template>

<script>
export default {
    props: ["PlayerLoadout"],
    data() {
        return {

        }
    },
    methods: {

    }
}
</script>

<style>
    .player {
        background-color: var(--box);
        box-sizing: border-box;
        width: 20%;
        margin: 50px auto 0 auto;
        padding: 15px 0;
        border-radius: 10px;
        /* border: solid 2.5px #ff4454; */
        cursor: pointer;
        transition-duration: 0.3s;
    }

    .player:hover  {
        background-color: #9c9c9c;
        /* border: solid 2.5px #992933; */
    }

    .player_name > span {
        color: #000;
        font-size: 1.5em;
    }

</style>