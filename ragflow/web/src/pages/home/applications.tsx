import { IconFont } from '@/components/icon-font';
import { Segmented, SegmentedValue } from '@/components/ui/segmented';
import { Routes } from '@/routes';
import { useCallback, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'umi';
import { SeeAllAppCard } from './application-card';
import { ChatList } from './chat-list';

const IconMap = {
  [Routes.Chats]: 'chat',
};

export function Applications() {
  const [val, setVal] = useState(Routes.Chats);
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleNavigate = useCallback(() => {
    navigate(val);
  }, [navigate, val]);

  const options = useMemo(
    () => [
      { value: Routes.Chats, label: t('chat.chatApps') },
    ],
    [t],
  );

  const handleChange = (path: SegmentedValue) => {
    setVal(path as string);
  };

  return (
    <section className="mt-12">
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-2xl font-bold flex gap-2.5">
          <IconFont
            name={IconMap[val as keyof typeof IconMap]}
            className="size-8"
          ></IconFont>
          {options.find((x) => x.value === val)?.label}
        </h2>
        <Segmented
          options={options}
          value={val}
          onChange={handleChange}
          className="bg-bg-card border border-border-button rounded-full"
          activeClassName="bg-text-primary border-none"
        ></Segmented>
      </div>
      <div className="flex flex-wrap gap-4">
        {val === Routes.Chats && <ChatList></ChatList>}
        {<SeeAllAppCard click={handleNavigate}></SeeAllAppCard>}
      </div>
    </section>
  );
}
