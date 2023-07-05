const ModalFactory = window.ModalFactory;

  ModalFactory.create({
    id: 'test-dialog',
    title: 'Hello',
    content: '<p>Hello</p>',
    buttons: [
      {
        name: 'Cancel',
        type: ModalFactory.ButtonTypes.REJECT,
        html: `<button class="secondary-btn text-accent-darkest bold washed-accent" id="cancel-button"></button>`,
      },
      {
        name: 'Reject',
        type: ModalFactory.ButtonTypes.REJECT,
        html: `<button class="secondary-btn text-accent-darkest bold washed-accent" id="reject-button"></button>`,
      },
      {
        name: 'Confirm',
        type: ModalFactory.ButtonTypes.CONFIRM,
        html: `<button class="primary-btn text-accent-darkest bold secondary-accent" id="confirm-button"></button>`,
      },
      {
        name: 'Accept',
        type: ModalFactory.ButtonTypes.CONFIRM,
        html: `<button class="primary-btn text-accent-darkest bold secondary-accent" id="accept-button"></button>`,
      },
    ]
  })
  .then((result) => {
    // e.g. user pressed a button that has type=ModalFactory.ButtonTypes.CONFIRM
    const name = result.name;
    if (name == 'Confirm') {
      console.log('[success] user confirmed', result);
    } else if (name == 'Accept') {
      console.log('[success] user accepted', result);
    }
  })
  .catch((result) => {
    // An error occurred somewhere (unrelated to button input)
    if (!(result instanceof ModalFactory.ModalResults)) {
      return console.error(result);
    }
  
    // e.g. user pressed a button that has type=ModalFactory.ButtonTypes.REJECT
    const name = result.name;
    if (name == 'Cancel') {
      console.log('[failure] user cancelled', result);
    } else if (name == 'Reject') {
      console.log('[failure] rejected', result);
    }
  });

  