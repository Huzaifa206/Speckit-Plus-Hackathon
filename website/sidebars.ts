import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Manual sidebar structure for the Physical AI & Humanoid Robotics book
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Foundations of Physical AI & Embodied Intelligence',
      link: {type: 'doc', id: 'chapter-1/intro'},
      items: [
        'chapter-1/intro',
        'chapter-1/lesson-1-physical-ai',
        'chapter-1/lesson-2-ros2',
        'chapter-1/lesson-3-digital-twins'
      ],
    },
  ],
};

export default sidebars;