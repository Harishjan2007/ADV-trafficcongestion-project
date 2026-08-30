/* Ambient type declarations for IDE and TypeScript compilation without node_modules */

declare global {
  namespace React {
    export interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {
      type: T;
      props: P;
      key: any;
    }
    export type JSXElementConstructor<P> = ((props: P) => ReactElement<any, any> | null) | (new (props: P) => any);
    export type FC<P = {}> = (props: P) => ReactElement<any, any> | null;
    export type ReactNode = any;
    export interface ChangeEvent<T = Element> {
      target: T & { value: string; checked?: boolean };
    }
    export function useState<T>(initial: T | (() => T)): [T, (val: T | ((prev: T) => T)) => void];
    export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
    export function useMemo<T>(factory: () => T, deps: any[] | undefined): T;
    export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
    export function useRef<T>(initialValue?: T): { current: T };
    export const StrictMode: FC<{ children?: any }>;
  }

  namespace JSX {
    interface Element extends React.ReactElement<any, any> {}
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

declare module 'react' {
  export = React;
}

declare module 'react-dom/client' {
  export function createRoot(container: Element | DocumentFragment): {
    render(children: any): void;
    unmount(): void;
  };
}

declare module 'react/jsx-runtime' {
  export function jsx(type: any, props: any, key?: any): any;
  export function jsxs(type: any, props: any, key?: any): any;
  export const Fragment: any;
}

declare module 'zustand' {
  export type StateCreator<T> = (
    set: (partial: T | Partial<T> | ((state: T) => T | Partial<T>), replace?: boolean) => void,
    get: () => T,
    api: any
  ) => T;
  export function create<T>(initializer: StateCreator<T>): {
    (): T;
    <U>(selector: (state: T) => U, equalityFn?: (a: U, b: U) => boolean): U;
    getState: () => T;
    setState: (partial: T | Partial<T> | ((state: T) => T | Partial<T>), replace?: boolean) => void;
    subscribe: (listener: (state: T, prevState: T) => void) => () => void;
  };
}

declare module 'lucide-react' {
  export interface IconProps {
    color?: string;
    size?: string | number;
    strokeWidth?: string | number;
    className?: string;
    style?: any;
  }
  export const Navigation: React.FC<IconProps>;
  export const Play: React.FC<IconProps>;
  export const Pause: React.FC<IconProps>;
  export const Sparkles: React.FC<IconProps>;
  export const MoveRight: React.FC<IconProps>;
  export const Activity: React.FC<IconProps>;
  export const Radio: React.FC<IconProps>;
  export const MapPin: React.FC<IconProps>;
  export const AlertTriangle: React.FC<IconProps>;
  export const X: React.FC<IconProps>;
  export const Layers: React.FC<IconProps>;
  export const Shield: React.FC<IconProps>;
  export const Clock: React.FC<IconProps>;
}

declare module 'vite' {
  export function defineConfig(config: any): any;
}

declare module '@vitejs/plugin-react' {
  export default function react(options?: any): any;
}
