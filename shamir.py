import secrets
import argparse

# Some cool prime for modulo calculations :)
P = 9223372036854775783

def modinv(a, p):
    # p must be a prime
    return pow(a, p-2, p)

secure_rng = secrets.SystemRandom()

def make_shares(secret, k, n, p):
    coefs = [secret] + [secure_rng.randrange(1, p) for _ in range(k-1)]

    def f(x):
        return sum(coefs[i] * pow(x, i, p) for i in range(k)) % p

    shares = [(x, f(x)) for x in range(1, n+1)]
    
    return shares

def reconstruct_secret(shares, p):
    secret = 0

    # We use Lagrange interpolation here
    for j, (xj, yj) in enumerate(shares):
        num = 1
        den = 1

        for m, (xm, _) in enumerate(shares):
            if m != j:
                num = (num * (-xm)) % p
                den = (den * (xj - xm)) % p

        lagrange_coef = num * modinv(den, p)
        secret = (secret + yj * lagrange_coef) % p

    return secret

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Shamir\'s Secret Sharing algorithm implementation')
    subparsers = parser.add_subparsers(dest='command', required=True)

    make_parser = subparsers.add_parser('make', help='Make shares')
    make_parser.add_argument('total_shares', type=int, help='Total number of shares')
    make_parser.add_argument('threshold', type=int, help='Threshold')
    make_parser.add_argument('secret', type=int)

    reconstruct_parser = subparsers.add_parser('reconstruct', help='Reconstruct secret from shares')
    reconstruct_parser.add_argument('threshold', type=int, help='Threshold')
    reconstruct_parser.add_argument('--shares', nargs='+', help='Shares to use represented as x_value,y_value')

    args = parser.parse_args()

    if args.command == 'make':
        n = args.total_shares
        k = args.threshold
        secret = args.secret

        print('=== Make ===')
        print(f'total_shares = {n}')
        print(f'   threshold = {k}')
        print(f'      secret = {secret}')

        shares = make_shares(secret, k, n, P)

        print('\nShares:')
        for share in shares:
            print(f'{share[0]},{share[1]}')

    elif args.command == 'reconstruct':
        k = args.threshold
        shares = args.shares
        n_shares = len(shares)

        if n_shares < k:
            print(f'Warning: The number of shares ({n_shares}) is lower than the threshold ({k}). The reconstructed secret will be wrong, but we continue anyway for the sake of education.\n')

        xy_shares = []
        for share in shares:
            split = share.split(',')
            xy = (int(split[0]), int(split[1]))

            if xy[1] is None:
                print(f'Error: Syntax for shares is "x_value,y_value", but got {share}')
                exit(2)

            xy_shares.append(xy)

        print('=== Reconstruct ===')
        print(f'threshold = {k}')
        print('\nShares:')
        for x, y in xy_shares:
            print(f'{x},{y}')

        secret = reconstruct_secret(xy_shares, P)

        print('\nSecret:')
        print(secret)
        
