<template>
  <div>
    <div class="row-outer" style="border-bottom: none;padding-right: 10px;">
      <button style="width: 100%; padding: 0.4em; color: blue;" @click.stop.prevent="doApply">Do Inspect</button>
    </div>
    <div class="row-outer" style="border-bottom: none;padding-right: 10px;">
      <input type="text" placeholder="Filter tags" v-model="filterStr"
        style="flex: 1;
          padding: 5px 2px;
          border: none;
          border-bottom: 1px solid #ccc;">
    </div>
    <div style="overflow-y: auto; height:400px;">
      <div class="row-outer" v-for="(tag, idx) in args.tags" :key="idx" v-show="tag.includes(filterStr)">
        <div class="tooltip" style="flex: 1;font-size: 0.75em; font-style: italic">
          <span class="tooltiptext">{{args.tagDescriptions[idx]}}</span>
          <span style="margin-right: 0.3em">{{idx + 1}}.</span>{{ tag }}
        </div>
        <div class='tag-item' :class="{'tag-active': dNFlags[idx], 'tag-disabled': args.nMasks[idx]}"
            @click="toggle(idx, 1)">N</div>
        <div class='tag-item' :class="{'tag-active': dOFlags[idx], 'tag-disabled': args.oMasks[idx]}"
            @click="toggle(idx, 2)">O</div>
        <div class='tag-item' :class="{'tag-active': dIFlags[idx], 'tag-disabled': args.iMasks[idx]}"
            @click="toggle(idx, 3)">I</div>
        <div class='tag-item' :class="{'tag-active': dFFlags[idx], 'tag-disabled': args.fMasks[idx]}"
            @click="toggle(idx, 4)">F</div>
      </div>
    </div>
  </div>
</template>

<style>
  .tooltip {
    position: relative;
  }
  .tooltip:hover {
    color: #0000ffab;
  }
  .tooltip .tooltiptext {
    visibility: hidden;
    width: 120px;
    background-color: wheat;
    color: #007;
    text-align: center;
    padding: 5px 0;
    border-radius: 4px;
    border: 1px solid #007;
   
    /* Position the tooltip text - see examples below! */
    position: absolute;
    top: 0;
    left: 0;
    transform: translateY(-100%);
    z-index: 1;
  }

  /* Show the tooltip text when you mouse over the tooltip container */
  .tooltip:hover .tooltiptext {
    visibility: visible;
  }
  .row-outer {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 5px;
    border-bottom: 1px solid #eee;
    border-radius: 5px;
  }
  .row-outer:first-child .tooltip:hover .tooltiptext {
    bottom: 0;
    left: 0;
    transform: translateY(100%);
    min-height: 1.2em;
  }
  
  .tag-item {
    cursor: pointer;
    border: 1px solid #444;
    padding: 2px 4px;
    border-radius: 3px;
    color: #444;
    margin-right: 5px;
    width: 1em;
    font-size: 0.75em;
    text-align: center;
  }
  .tag-active {
    color: white;
    background: #0000ffab;
    border-color: white;
  }
  .tag-disabled {
    pointer-events: none;
    color: #eee;
    border-color: #eee;
  }
</style>
<script>
import { ref } from "vue"
import { Streamlit } from "streamlit-component-lib"
import { useStreamlit } from "./streamlit"

export default {
  name: "TagList",
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in prop "args"
  data() {
    return {
      filterStr: "",
      dNFlags: [],
      dOFlags: [],
      dIFlags: [],
      dFFlags: [],
    }
  },
  mounted() {
    this.dNFlags = new Array(this.args.nMasks.length).fill(false);
    this.dOFlags = new Array(this.args.nMasks.length).fill(false);
    this.dIFlags = new Array(this.args.nMasks.length).fill(false);
    this.dFFlags = new Array(this.args.nMasks.length).fill(false);
  },
  methods: {
    toggle(tagIdx, checkIdx) {
      for (let i = 0; i < this.dNFlags.length ; i++) {
        if (tagIdx === i) continue;
        this.dNFlags[i] = false;
        this.dOFlags[i] = false;
        this.dIFlags[i] = false;
        this.dFFlags[i] = false;
      }
      switch(checkIdx) {
        case 1: 
          this.dNFlags[tagIdx] = !this.dNFlags[tagIdx];
          return;
        case 2: 
          this.dOFlags[tagIdx] = !this.dOFlags[tagIdx];
          return;
        case 3: 
          this.dIFlags[tagIdx] = !this.dIFlags[tagIdx];
          return;
        case 4: 
          this.dFFlags[tagIdx] = !this.dFFlags[tagIdx];
          return;
      }
    },
    doApply() {
      const nIdx = this.dNFlags.findIndex(flag => flag);
      const oIdx = this.dOFlags.findIndex(flag => flag);
      const iIdx = this.dIFlags.findIndex(flag => flag);
      const fIdx = this.dFFlags.findIndex(flag => flag);
      Streamlit.setComponentValue({nIdx, oIdx, iIdx, fIdx });
    }
  },
  setup() {
    useStreamlit() // lifecycle hooks for automatic Streamlit resize

    const numClicks = ref(0)
    const onClicked = () => {
      numClicks.value++
      Streamlit.setComponentValue(numClicks.value)
    }

    return {
      numClicks,
      onClicked,
    }
  },
}
</script>
