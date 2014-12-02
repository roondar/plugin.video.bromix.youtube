__author__ = 'bromix'


def append_subscribe_to_channel(context_menu, provider, context, channel_id, channel_name=u''):
    text = u''
    if channel_name:
        text = context.localize(provider.LOCAL_MAP['youtube.subscribe_to']).replace('%s', '[B]' + channel_name + '[/B]')
        context_menu.append(
            (text, 'RunPlugin(%s)' % context.create_uri(['subscriptions', 'add'], {'subscription_id': channel_id})))
        pass
    else:
        context_menu.append((context.localize(provider.LOCAL_MAP['youtube.subscribe']),
                             'RunPlugin(%s)' % context.create_uri(['subscriptions', 'add'],
                                                                  {'subscription_id': channel_id})))
        pass
    pass


def append_unsubscribe_from_channel(context_menu, provider, context, channel_id, channel_name=u''):
    context_menu.append((context.localize(provider.LOCAL_MAP['youtube.unsubscribe']),
                         'RunPlugin(%s)' % context.create_uri(['subscriptions', 'remove'],
                                                              {'subscription_id': channel_id})))
    pass