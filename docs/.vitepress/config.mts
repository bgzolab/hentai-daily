import { defineConfig } from 'vitepress'
import taskLists from 'markdown-it-task-lists'


// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Hentai Daily",
  description: "Hentai contents combined with multi sources daily",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      {text: 'Home', link: '/'},
      {text: 'Today', link: '/today'},
      {text: 'Changelog', link: '/changelog'},
    ],

    // sidebar: [
    //   {
    //     text: 'Examples',
    //     items: [
    //       { text: 'Markdown Examples', link: '/markdown-examples' },
    //       { text: 'Runtime API Examples', link: '/api-examples' }
    //     ]
    //   }
    // ],

    socialLinks: [
      {icon: 'github', link: 'https://github.com/bGZo/hentai-daily'}
    ],
  },

  // via: https://github.com/vuejs/vitepress/issues/1923#issuecomment-1431479500
  markdown: {
    config: (md) => {
      md.use(taskLists, {
        disabled: false,
        divWrap: false,
        divClass: 'checkbox',
        idPrefix: 'cbx_',
        ulClass: 'task-list',
        liClass: 'task-list-item'
      })
    }
  },

})
